import base64
import hashlib
import hmac
import os

from boto.s3.connection import Key, S3Connection
from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    jsonify,
)
from flask_security import login_required
from funcy import none
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


@upload.route('s3/sign', methods=['POST'])
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
            amz_credential = "no_client_id/"+headers.split('\n')[2]
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
        return jsonify(
            error="There was an error generating the AWS signature"), 500

    return jsonify(
        policy=(policy.decode() if conditions else ''),
        signature=signature.hexdigest(),
    )


@upload.route("s3/delete/<key>", methods=['POST', 'DELETE'])
@login_required
def s3_delete(key=None):
    """ Route for deleting files off S3. Uses the SDK. """
    request_payload = request.values
    key_name = request_payload.get('key')
    bucket_name = request_payload.get('bucket')
    assert bucket_name == S3_BUCKET

    # TODO: check if this user is the owner of the file,
    # and thus allowed to delete it
    # bonus points for using ACL decorator

    s3 = S3Connection(
        S3_MANAGER_PUBLIC_KEY,
        S3_MANAGER_SECRET_KEY
    )
    aws_bucket = s3.get_bucket(bucket_name, validate=False)
    aws_key = Key(aws_bucket, key_name)
    aws_key.delete()
    return make_response('', 200)


@upload.route("s3/success", methods=['GET', 'POST'])
def s3_success():
    # TODO: do something...
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
