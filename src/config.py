from os import getenv


def load_json_config(name):
    import json
    env = 'prod' if getenv('PRODUCTION') else 'dev'
    return json.loads(open(f'src/conf/{name}.{env}.json', 'r').read())


# base config
SECRET_KEY = getenv('SECRET_KEY', 'not_a_good_secret')
VIRTUAL_HOST = getenv('VIRTUAL_HOST', 'localhost:5000')

# amazon s3 manager credentials
S3_MANAGER_PUBLIC_KEY = getenv('S3_MANAGER_PUBLIC_KEY')
S3_MANAGER_PRIVATE_KEY = getenv('S3_MANAGER_PRIVATE_KEY')

# amazon s3 upload signatures
S3_UPLOADER_PUBLIC_KEY = getenv('S3_UPLOADER_PUBLIC_KEY')
S3_UPLOADER_PRIVATE_KEY = getenv('S3_UPLOADER_PRIVATE_KEY')
S3_UPLOADER_BUCKET = getenv('S3_UPLOADER_BUCKET', 'viewly-uploads-test')
S3_UPLOADER_REGION = getenv('S3_UPLOADER_REGION', 'us-west-2')

# amazon s3 processed assets (videos, thumbnails, etc.) location
S3_VIDEOS_BUCKET = getenv('S3_ASSETS_BUCKET', 'viewly-videos-test')
S3_VIDEOS_REGION = getenv('S3_VIDEOS_REGION', 'us-west-2')

# videos and thumbnails CDN
CDN_URL = getenv('CDN_URL', 'http://cdn.view.ly')

# PostgreSQL
SQLALCHEMY_DATABASE_URI = getenv('POSTGRES_URI', 'postgres://localhost/viewly_beta')
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
SECURITY_CONFIRMABLE = bool(getenv('PRODUCTION'))
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_PASSWORDLESS = False
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome to Viewly. Please confirm your email."

# Celery
CELERY_BACKEND_URL = getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

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
