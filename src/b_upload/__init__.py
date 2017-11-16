import base64
import datetime as dt
import hashlib
import hmac

import boto3
from botocore.exceptions import ClientError
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
from ..models import (
    Video,
    FileMapper,
    TranscoderStatus,
)
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
def index():
    pending_count = db.session.query(Video).filter_by(
        user_id=current_user.id,
        published_at=None,
    ).count()
    return render_template(
        'index.html',
        s3_bucket_name=app.config['S3_UPLOADER_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADER_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
        pending_count=pending_count,
    )


@upload.route('s3/sign', methods=['POST'])
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


@upload.route("s3/success", methods=['GET', 'POST'])
@can_upload
@login_required
def s3_success():
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


@upload.route("s3/delete/<string:key>", methods=['POST', 'DELETE'])
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
@upload.route("delete/<string:video_id>", methods=['POST', 'DELETE'])
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
class PublishForm(FlaskForm):
    title = StringField('Title of your Video', validators=[validators.DataRequired()])
    description = TextAreaField('Short Description (optional)')


@upload.route("publish/<string:video_id>", methods=['GET', 'POST'])
@login_required
def publish(video_id):
    """ Publish the last uploaded video """
    error = None
    form = PublishForm()

    # check if video is valid
    # and if user can publish it
    video = db.session.query(Video).filter_by(
        id=video_id,
        user_id=current_user.id,
    ).first()
    if not video:
        return redirect(url_for('.publish_list'))
    if video and not video.published_at:
        # set the upload file as title
        if not form.title.data:
            form.title.data = video.title

        # do some publishing here
        # redirect to video page
        if form.validate_on_submit():
            video.title = form.title.data
            video.description = form.description.data
            video.published_at = dt.datetime.utcnow()

            db.session.add(video)
            db.session.commit()

            return redirect(f'/v/{video.id}')

    return render_template(
        'publish-single.html',
        form=form,
        error=error,
        source=get_video_playback_url(video),
    )


@upload.route("publish")
@login_required
def publish_list():
    to_publish = db.session.query(Video).filter_by(
        user_id=current_user.id,
        published_at=None,
    ).order_by(desc(Video.uploaded_at)).all()

    if len(to_publish) == 0:
        return redirect(url_for('.index'))
    elif len(to_publish) == 1:
        video = first(to_publish)
        return redirect(url_for(".publish", video_id=video.id))

    return render_template(
        'publish-list.html',
        videos=to_publish,
    )


# Helpers
# -------
def delete_unpublished_video(video: Video):
    s3 = boto3.resource(
        's3',
        region_name=app.config['S3_UPLOADER_REGION'],
        aws_access_key_id=app.config['S3_MANAGER_PUBLIC_KEY'],
        aws_secret_access_key=app.config['S3_MANAGER_PRIVATE_KEY'],
    )
    try:
        obj = s3.Object(
            video.file_mapper.s3_upload_bucket,
            video.file_mapper.s3_upload_video_key,
        )
        obj.load()
        obj.delete()
    except ClientError:
        return make_response('S3 Error', 500)
    else:
        db.session.delete(video)
        db.session.commit()
    return make_response('', 200)


def s3_make_public(bucket_name: str, key: str):
    s3 = boto3.client(
        's3',
        region_name=app.config['S3_UPLOADER_REGION'],
        aws_access_key_id=app.config['S3_MANAGER_PUBLIC_KEY'],
        aws_secret_access_key=app.config['S3_MANAGER_PRIVATE_KEY'],
    )
    return s3.put_object_acl(
        ACL='public-read',
        Bucket=bucket_name,
        Key=key
    )


def get_video_playback_url(video: Video):
    """ Get a video playback, regardless of transcoding status
    or the thumbnail availability.

    To be used with publishing preview player.
    """
    result = {
        'video': '',
        'poster': '',
    }
    s3_url_template = "https://s3.{region}.amazonaws.com/{bucket}/{key}"
    s3_upload_bucket_url = s3_url_template.format(
        region=app.config['S3_UPLOADER_REGION'],
        bucket=video.file_mapper.s3_upload_bucket,
        key='',
    )

    if video.transcoder_status == TranscoderStatus.complete:
        pass
    else:
        result['video'] = s3_upload_bucket_url + \
                          video.file_mapper.s3_upload_video_key

    if video.file_mapper.s3_upload_thumbnail_key:
        result['poster'] = s3_upload_bucket_url + \
                           video.file_mapper.s3_upload_thumbnail_key

    return result
