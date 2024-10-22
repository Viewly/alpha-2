import base64
import datetime as dt
import hashlib
import hmac

import boto3
from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    jsonify,
    redirect,
    url_for,
)
from flask_security import login_required, current_user
from flask_wtf import FlaskForm
from funcy import none, decorator, first, suppress
from sqlalchemy import desc
from toolz import thread_first
from wtforms import (
    StringField,
    validators,
    TextAreaField,
)

from .. import app, db
from ..core.et import cancel_job
from ..core.eth import null_address
from ..methods import get_thumbnail_cdn_url
from ..models import (
    Video,
    FileMapper,
    Channel,
    Wallet,
    TranscoderJob,
    VideoFrameAnalysis,
    TranscoderStatus,
)
from ..tasks.shared import delete_video_files
from ..tasks.thumbnails import process_thumbnails, process_avatar
from ..tasks.transcoder import start_transcoder_job

upload = Blueprint(
    'upload',
    __name__,
    template_folder='templates'
)


@decorator
def can_upload(fn):
    if not current_user.can_upload:
        return make_response('Not Allowed', 405)
    return fn()


# Upload
# ------
@upload.route('/')
@login_required
def upload_videos():
    pending_count = db.session.query(Video).filter_by(
        user_id=current_user.id,
        published_at=None,
    ).count()
    return render_template(
        'upload-videos.html',
        s3_bucket_name=app.config['S3_UPLOADS_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADS_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
        pending_count=pending_count,
    )


@upload.route('/s3/sign', methods=['POST'])
@can_upload
@login_required
def s3_signature():
    policy = base64.b64encode(request.data)
    conditions = request.get_json().get('conditions')
    headers = request.get_json().get('headers')

    if none([headers, conditions]):
        return jsonify(invalid=True), 500

    def find_condition(key):
        from funcy import first
        return first(x[key] for x in conditions if key in x)

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def calc_signature(secret_key, _, datestamp, region, service, aws_request):
        # assert service == 's3'  # this shouldn't be a problem if AMI was setup right
        return thread_first(
            f'AWS4{secret_key}'.encode('utf-8'),
            (sign, datestamp),
            (sign, region),
            (sign, service),
            (sign, aws_request),
        )

    try:
        if conditions:
            amz_credential = find_condition('x-amz-credential')
        else:
            amz_credential = "no_client_id/" + headers.split('\n')[2]
            policy_data, policy_data_hash = headers.split('/s3/aws4_request\n')
            policy_data_hash = hashlib.sha256(policy_data_hash.encode()).hexdigest()
            policy = f'{policy_data}/s3/aws4_request\n{policy_data_hash}'.encode()

        if not amz_credential:
            return jsonify(invalid=True), 500

        signing_key = calc_signature(
            app.config['S3_UPLOADER_PRIVATE_KEY'],
            *amz_credential.split('/')
        )

        signature = hmac.new(signing_key, policy, hashlib.sha256)
    except:
        resp = jsonify(
            error="There was an error generating the AWS signature"), 500
    else:
        resp = jsonify(
            policy=(policy.decode() if conditions else ''),
            signature=signature.hexdigest(),
        )
    return resp


@upload.route("/s3/success", methods=['GET', 'POST'])
@can_upload
@login_required
def s3_success():
    # defensively prevent duplicates
    # if s3_success is called multiple times for same upload, ignore
    if db.session.query(FileMapper) \
            .filter_by(s3_upload_video_key=request.form.get('key')).first():
        return {}

    video = Video(
        user_id=current_user.id,
        title=request.form.get('name').split('.')[0],
        uploaded_at=dt.datetime.utcnow(),
    )
    video.file_mapper = FileMapper(
        s3_upload_bucket=request.form.get('bucket'),
        s3_upload_video_key=request.form.get('key'),
    )
    db.session.add(video)
    db.session.commit()

    # start the transcoding job
    start_transcoder_job.delay(video.id)

    # if the bucket policy were public, we wouldn't need this
    with suppress(Exception):
        s3_make_public(
            video.file_mapper.s3_upload_bucket,
            video.file_mapper.s3_upload_video_key
        )

    return jsonify(
        video_id=video.id,
    )


@upload.route("/s3/thumb_success", methods=['GET', 'POST'])
@can_upload
@login_required
def s3_thumb_success():
    video = Video.query.filter_by(
        user_id=current_user.id,
        id=request.form.get('video_id'),
    ).first_or_404()
    video.file_mapper.s3_upload_thumbnail_key = request.form.get('key')
    db.session.add(video)
    db.session.commit()

    # start the thumbnail resizing
    process_thumbnails.delay(video.id)

    # if the bucket policy were public, we wouldn't need this
    with suppress(Exception):
        s3_make_public(
            video.file_mapper.s3_upload_bucket,
            video.file_mapper.s3_upload_thumbnail_key
        )

    return jsonify(
        video_id=video.id,
    )


@upload.route("/s3/avatar_success", methods=['GET', 'POST'])
@login_required
def s3_avatar_success():
    channel = Channel.query.filter_by(
        user_id=current_user.id,
        id=request.form.get('channel_id'),
    ).first_or_404()

    profile = channel.profile or {}
    profile['s3_avatar_key'] = request.form.get('key')

    channel.profile = profile
    db.session.add(channel)
    db.session.commit()

    # start the thumbnail resizing
    process_avatar.delay(channel.id)

    # if the bucket policy were public, we wouldn't need this
    with suppress(Exception):
        s3_make_public(app.config['S3_UPLOADS_BUCKET'], profile['s3_avatar_key'])

    return jsonify(
        channel_id=channel.id,
    )


@upload.route("/s3/delete/<string:key>", methods=['POST', 'DELETE'])
@login_required
def s3_delete(key):
    """ Route for deleting files off S3. Uses the SDK. """
    request_payload = request.values
    s3_key = request_payload.get('key')
    s3_bucket = request_payload.get('bucket')

    # check if current_user owns the key in Uploads,
    # and if so; he is allowed to delete it
    sub_query = db.session.query(FileMapper.video_id) \
        .filter_by(s3_upload_bucket=s3_bucket, s3_upload_video_key=s3_key) \
        .subquery()
    video = current_user.videos.filter_by(id=sub_query).first()
    if not video:
        return make_response('Not Allowed', 405)

    return delete_unpublished_video(video)


# Delete
# ------
@upload.route("/delete/<string:video_id>", methods=['POST', 'DELETE'])
@login_required
def delete_video(video_id):
    """ Delete unpublished video from S3 and database. """
    video = current_user.videos.filter_by(
        id=video_id,
        user_id=current_user.id,
        published_at=None).first()
    if not video:
        return make_response('Not Allowed', 405)

    return delete_unpublished_video(video)


# Publish
# -------
class AddDetailsForm(FlaskForm):
    title = StringField('Pick a title for your video',
                        validators=[validators.DataRequired()])
    description = TextAreaField('Short description')


@upload.route("/publish/add_details/<string:video_id>", methods=['GET', 'POST'])
@login_required
def publish_add_details(video_id):
    """ Publish the last uploaded video """
    error = None
    form = AddDetailsForm()

    # check if video is valid
    # and if user can publish it
    video = db.session.query(Video).filter_by(
        id=video_id,
        user_id=current_user.id,
    ).first()
    if video:
        if not form.title.data:
            form.title.data = video.title
        if not form.description.data:
            form.description.data = video.description

        # do some publishing here
        # redirect to video page
        if form.validate_on_submit():
            video.title = form.title.data
            video.description = form.description.data
            db.session.add(video)
            db.session.commit()

            # return redirect(f'/v/{video.id}')
    else:
        return redirect(url_for('.publish_list_uploads'))

    return render_template(
        'publish-add-details.html',
        form=form,
        error=error,
        video=video,
    )


@upload.route("/publish/add_thumbnails/<string:video_id>", methods=['GET', 'POST'])
@login_required
def publish_add_thumbnails(video_id):
    """ Handle Thumbnail Uploads """
    error = None

    # check if video is valid
    # and if user can publish it
    video = db.session.query(Video).filter_by(
        id=video_id,
        user_id=current_user.id,
    ).first()
    if not video:
        return redirect(url_for('.publish_list_uploads'))

    return render_template(
        'publish-add-thumbnails.html',
        video=video,
        error=error,
        current_thumbnail=get_thumbnail_cdn_url(video, 'tiny'),
        s3_bucket_name=app.config['S3_UPLOADS_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADS_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
    )


@upload.route("/publish/to_channel/<string:video_id>", methods=['GET', 'POST'])
@login_required
def publish_to_channel(video_id):
    """ Publish the last uploaded video """
    # and if user can publish it
    video = db.session.query(Video).filter_by(
        id=video_id,
        user_id=current_user.id,
    ).first()
    if not video:
        return redirect(url_for('.publish_list_uploads'))
    if video.channel_id:
        return redirect(url_for('.publish_to_ethereum', video_id=video.id))
    if video.published_at:
        return redirect(f'/v/{video.id}')

    if request.method == 'POST':
        video.channel_id = request.form['channel_id']
        assert db.session.query(Channel).filter_by(
            id=video.channel_id,
            user_id=current_user.id,
        ).first()
        # video.published_at = dt.datetime.utcnow()
        db.session.add(video)
        db.session.commit()
        return jsonify(video_id=video.id)

    channels = db.session.query(Channel).filter_by(
        user_id=current_user.id,
    ).all()

    return render_template(
        'publish-to-channel.html',
        video=video,
        channels=channels,
    )


@upload.route("/publish/to_ethereum/<string:video_id>", methods=['GET'])
@login_required
def publish_to_ethereum(video_id):
    """ Publish the last uploaded video """
    video = db.session.query(Video).filter_by(
        id=video_id,
        user_id=current_user.id,
    ).first()
    if not video:
        return redirect(url_for('.publish_list_uploads'))
    if video.published_at:
        return redirect(f'/v/{video.id}')

    # special case - if its their first video, publish it for free
    num_videos = db.session.query(Video).filter_by(
        user_id=current_user.id,
    ).count()
    eth_address = null_address
    with suppress(Exception):
        wallet = db.session.query(Wallet).filter_by(
            user_id=current_user.id,
        ).order_by(desc(Wallet.created_at)).first()
        eth_address = wallet.default_address
    if num_videos == 0:
        video.published_at = dt.datetime.utcnow()
        video.eth_address = eth_address
        db.session.add(video)
        db.session.commit()
        return redirect(f'/v/{video.id}')

    return render_template(
        'publish-to-ethereum.html',
        video=video,
    )


@upload.route("/publish")
@login_required
def publish_list_uploads():
    to_publish = db.session.query(Video).filter_by(
        user_id=current_user.id,
        published_at=None,
    ).order_by(desc(Video.uploaded_at)).all()

    if len(to_publish) == 0:
        return redirect(url_for('.upload_videos'))
    elif len(to_publish) == 1:
        video = first(to_publish)
        return redirect(url_for(".publish_add_details", video_id=video.id))

    return render_template(
        'publish-list-uploads.html',
        videos=to_publish,
    )


# Helpers
# -------
def delete_unpublished_video(video: Video):
    file_mapper_obj = dict(
        s3_upload_bucket=video.file_mapper.s3_upload_bucket,
        s3_upload_video_key=video.file_mapper.s3_upload_video_key,
        s3_upload_thumbnail_key=video.file_mapper.s3_upload_thumbnail_key,
    )
    delete_video_sql(video.id)
    # cleanup actual files in 1 hour
    # in case of delete being triggered in the middle of post-processing
    delete_video_files.apply_async((video.id, file_mapper_obj), countdown=3600)
    return make_response('', 200)


def delete_video_sql(video_id):
    video = db.session.query(Video).filter_by(id=video_id).one()
    assert video.published_at is None, 'Cannot delete a published video'

    # cancel transcoding jobs
    for job in db.session.query(TranscoderJob).filter_by(video_id=video.id):
        if job.status in (TranscoderStatus.pending, TranscoderStatus.processing):
            with suppress(Exception):
                cancel_job(job.id)

    # delete orphaned (non-cascading entries)
    db.session.query(TranscoderJob).filter_by(video_id=video_id).delete()
    db.session.query(VideoFrameAnalysis).filter_by(video_id=video_id).delete()

    db.session.delete(video)
    db.session.commit()


def s3_make_public(bucket_name: str, key: str):
    """
    Make an S3 file publicly visible (although unlisted).
    This is not necessary if all files are publicly readable by default bucket policy.
    """
    s3 = boto3.client(
        's3',
        region_name=app.config['S3_UPLOADS_REGION'],
        aws_access_key_id=app.config['AWS_MANAGER_PUBLIC_KEY'],
        aws_secret_access_key=app.config['AWS_MANAGER_PRIVATE_KEY'],
    )
    return s3.put_object_acl(
        ACL='public-read',
        Bucket=bucket_name,
        Key=key
    )
