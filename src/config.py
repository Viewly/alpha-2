import json
from os import getenv

from toolz import pipe

IS_PRODUCTION = bool(getenv('PRODUCTION', False))

# base config
SECRET_KEY = getenv('SECRET_KEY', 'not_a_good_secret')

# needed for Disqus plugin, shared /w nginx reverse proxy
VIRTUAL_HOST = getenv('VIRTUAL_HOST', 'http://localhost:5000')

# amazon manager credentials
AWS_MANAGER_PUBLIC_KEY = getenv('AWS_MANAGER_PUBLIC_KEY')
AWS_MANAGER_PRIVATE_KEY = getenv('AWS_MANAGER_PRIVATE_KEY')

# amazon s3 upload signatures
S3_UPLOADER_PUBLIC_KEY = getenv('S3_UPLOADER_PUBLIC_KEY')
S3_UPLOADER_PRIVATE_KEY = getenv('S3_UPLOADER_PRIVATE_KEY')

# amazon s3 upload bucket
S3_UPLOADS_BUCKET = getenv('S3_UPLOADS_BUCKET')
S3_UPLOADS_REGION = getenv('S3_UPLOADS_REGION')

# amazon s3 processed assets (videos, thumbnails, etc.) location
S3_VIDEOS_BUCKET = getenv('S3_VIDEOS_BUCKET')
S3_VIDEOS_REGION = getenv('S3_VIDEOS_REGION')

# amazon Cloud Formation distribution ID
CDN_DISTRIBUTION_ID = getenv('CDN_DISTRIBUTION_ID')

# videos and thumbnails CDN
CDN_URL = getenv('CDN_URL', 'https://cdn.view.ly')

# PostgreSQL
SQLALCHEMY_DATABASE_URI = getenv('POSTGRES_URL', 'postgres://localhost/alpha')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_MAX_OVERFLOW = 200

# Email
MAIL_USERNAME = getenv('MAIL_USERNAME', 'postmaster@mg.view.ly')
MAIL_PASSWORD = getenv('MAIL_PASSWORD', '18e7f9181eeb08de7de059ae659e07c0')
MAIL_SERVER = getenv('MAIL_SERVER', 'smtp.mailgun.org')
MAIL_PORT = int(getenv('MAIL_PORT', 2525))
MAIL_DEFAULT_SENDER = ('Viewly Alpha', 'alpha@view.ly')

# Flask-Security
SECURITY_PASSWORD_SALT = ""
SECURITY_CONFIRMABLE = IS_PRODUCTION
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_PASSWORDLESS = False
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome to Viewly Alpha 2. Please confirm your email."

# Celery
CELERY_BACKEND_URL = getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# Ethereum chain
ETH_CHAIN = getenv('ETH_CHAIN')
INFURA_KEY = getenv('INFURA_KEY')

# Ethereum Contracts
VIEW_TOKEN_ADDRESS = getenv('VIEW_TOKEN_ADDRESS')
VIDEO_PUBLISHER_ADDRESS = getenv('VIDEO_PUBLISHER_ADDRESS')
VIDEO_PUBLISHER_ABI = \
    pipe('src/conf/VideoPublisher.json', open, lambda x: x.read(), json.loads)['abi']


def load_json_config(name):
    env = 'prod' if IS_PRODUCTION else 'dev'
    return json.loads(open(f'src/conf/{name}.{env}.json', 'r').read())


# Elastic Transcoder
elastic_transcoder = load_json_config('elastic_transcoder')

# potentially separate into classes
# then load with app.config.from_obj('config.Development')
#
# class Development:
#     SECRET_KEY = getenv(...)
#
# class Production:
#     SECRET_KEY = getenv(...)
