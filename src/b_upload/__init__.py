import datetime as dt
import hashlib
import hmac

from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
)
from flask_security import login_required
from toolz import thread_first

upload = Blueprint(
    'upload',
    __name__,
    template_folder='templates'
)


@upload.route('/')
@login_required
def index():
    return render_template('index.html')


@upload.route('/s3_sign')
@login_required
def s3_sign():
    to_sign = str(request.args.get('to_sign')).encode('utf-8')
    date_stamp = dt.datetime.strptime(
        request.args.get('datetime'),
        '%Y%m%dT%H%M%SZ',
    ).strftime('%Y%m%d')

    aws_secret = 'AWS_SECRET_KEY'
    region = 'AWS_REGION'
    service = 's3'

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature(key, timestamp, region_name, service_name):
        return thread_first(
            f'AWS4{key}'.encode('utf-8'),
            (sign, timestamp),
            (sign, region_name),
            (sign, service_name),
            (sign, 'aws4_request'),
        )

    signing_key = get_signature(aws_secret, date_stamp, region, service)

    signature = hmac.new(
        signing_key,
        to_sign,
        hashlib.sha256
    ).hexdigest()

    resp = make_response(signature)
    resp.headers['Content-Type'] = "text/plain"
    return resp
