import base64
import hashlib
import hmac
import os

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

upload = Blueprint(
    'upload',
    __name__,
    template_folder='templates'
)

# for s3 delete endpoint
S3_MANAGER_PUBLIC_KEY = os.getenv('S3_MANAGER_PUBLIC_KEY')
S3_MANAGER_SECRET_KEY = os.getenv('S3_MANAGER_SECRET_KEY')

# for s3 upload signatures
S3_UPLOADER_PUBLIC_KEY = os.getenv('S3_UPLOADER_PUBLIC_KEY')
S3_UPLOADER_SECRET_KEY = os.getenv('S3_UPLOADER_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET', 'flask-uploader-test')
S3_REGION = os.getenv('S3_REGION', 'eu-central-1')


@decorator
def can_upload(fn):
    if not current_user.can_upload:
        return make_response('Not Allowed', 405)
    return fn()


@decorator
def can_delete(fn):
    print(request.values.get('key'))
    # check if current_user owns the key in Uploads,
    # and if so; he is allowed to delete it
    return fn(key=fn.key)


@upload.route('s3/sign', methods=['POST'])
@login_required
@can_upload
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
            S3_UPLOADER_SECRET_KEY,
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
@can_delete
def s3_delete(key):
    """ Route for deleting files off S3. Uses the SDK. """
    request_payload = request.values
    key_name = request_payload.get('key')
    bucket_name = request_payload.get('bucket')
    assert bucket_name == S3_BUCKET, "Invalid Bucket"

    s3 = boto3.resource(
        's3',
        region_name=S3_REGION,
        aws_access_key_id=S3_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=S3_MANAGER_SECRET_KEY,
    )
    try:
        obj = s3.Object(S3_BUCKET, key_name)
        obj.load()
        obj.delete()
    except ClientError:
        pass
    return make_response('', 200)


@upload.route("s3/success", methods=['GET', 'POST'])
def s3_success():
    # TODO: do something...
    print(request.form.get('key'))
    print(request.form.get('uuid'))
    print(request.form.get('name'))
    print(request.form.get('bucket'))
    return make_response()


@upload.route('/')
@login_required
def index():
    return render_template(
        'index.html',
        s3_bucket_name=S3_BUCKET,
        s3_bucket_region=S3_REGION,
        s3_user_access_key=S3_UPLOADER_PUBLIC_KEY,
    )
