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
)
from flask_security import login_required, current_user
from funcy import none, decorator
from toolz import thread_first

from .. import app, db
from ..models import Video
from ..utils import keep

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


@upload.route("s3/delete/<string:key>", methods=['POST', 'DELETE'])
@login_required
def s3_delete(key):
    """ Route for deleting files off S3. Uses the SDK. """
    request_payload = request.values
    s3_key = request_payload.get('key')
    bucket_name = request_payload.get('bucket')
    assert bucket_name == app.config['S3_UPLOADER_BUCKET'], "Invalid Bucket"

    # check if current_user owns the key in Uploads,
    # and if so; he is allowed to delete it
    video = current_user.videos.filter_by(s3_input_key=s3_key).first()
    if not video:
        return make_response('Not Allowed', 405)

    s3 = boto3.resource(
        's3',
        region_name=app.config['S3_UPLOADER_REGION'],
        aws_access_key_id=app.config['S3_MANAGER_PUBLIC_KEY'],
        aws_secret_access_key=app.config['S3_MANAGER_PRIVATE_KEY'],
    )
    try:
        obj = s3.Object(app.config['S3_UPLOADER_BUCKET'], s3_key)
        obj.load()
        obj.delete()
    except ClientError:
        pass
    else:
        db.session.delete(video)
        db.session.commit()
    return make_response('', 200)


@upload.route("s3/success", methods=['GET', 'POST'])
@can_upload
@login_required
def s3_success():
    video = Video(
        user_id=current_user.id,
        s3_bucket_name=request.form.get('bucket'),
        s3_input_key=request.form.get('key'),
        title=request.form.get('name').split('.')[0],
        uploaded_at=dt.datetime.utcnow(),
    )
    db.session.add(video)
    db.session.commit()

    return jsonify(keep(
        video.__dict__,
        ['id', 's3_bucket_name', 's3_input_key']
    ))


@upload.route('/')
@login_required
def index():
    return render_template(
        'index.html',
        s3_bucket_name=app.config['S3_UPLOADER_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADER_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
    )
