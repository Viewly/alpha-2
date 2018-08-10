import json
from os import getenv, environ, getcwd, path
from dotenv import load_dotenv, find_dotenv

from funcy import rpartial
from toolz import pipe

load_json_file = rpartial(pipe, open, lambda x: x.read(), json.loads)


def config_folder_prefix():
    # todo: improve this quick hack
    # (currently tightly coupled to alpha-2 folder)
    # It should find the correct config file path when
    # ran from src/, tests/ or Docker based paths.
    return path.join(getcwd().split('alpha-2')[0], 'alpha-2/config')


def load_json_config(name):
    env = 'prod' if IS_PRODUCTION else 'dev'
    return load_json_file(f'{config_folder_prefix()}/{name}.{env}.json')


# load default config
IS_PRODUCTION = bool(getenv('PRODUCTION', False))
if not IS_PRODUCTION:
    load_dotenv(find_dotenv())
FLASK_ENV = environ['FLASK_ENV'].lower()

# base config
SECRET_KEY = getenv('SECRET_KEY', 'not_a_good_secret')

# needed for Disqus plugin, shared /w nginx reverse proxy
VIRTUAL_HOST = getenv('VIRTUAL_HOST', 'http://localhost:5000')

# amazon manager credentials
AWS_MANAGER_PUBLIC_KEY = environ['AWS_MANAGER_PUBLIC_KEY']
AWS_MANAGER_PRIVATE_KEY = environ['AWS_MANAGER_PRIVATE_KEY']

# amazon s3 upload signatures
S3_UPLOADER_PUBLIC_KEY = environ['S3_UPLOADER_PUBLIC_KEY']
S3_UPLOADER_PRIVATE_KEY = environ['S3_UPLOADER_PRIVATE_KEY']

# amazon s3 upload bucket
S3_UPLOADS_BUCKET = environ['S3_UPLOADS_BUCKET']
S3_UPLOADS_REGION = environ['S3_UPLOADS_REGION']

# amazon s3 processed assets (videos, thumbnails, etc.) location
S3_VIDEOS_BUCKET = environ['S3_VIDEOS_BUCKET']
S3_VIDEOS_REGION = environ['S3_VIDEOS_REGION']

# amazon Cloud Formation distribution ID
CDN_DISTRIBUTION_ID = environ['CDN_DISTRIBUTION_ID']

# videos and thumbnails CDN
CDN_URL = getenv('CDN_URL', 'https://cdn.view.ly')

# player url
PLAYER_URL = getenv('PLAYER_URL', 'https://player.view.ly')

# PostgreSQL
SQLALCHEMY_DATABASE_URI = getenv('POSTGRES_URL', 'postgres://localhost/alpha')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_MAX_OVERFLOW = 200

# Email
MAIL_SERVER = getenv('MAIL_SERVER', 'smtp.mandrillapp.com')
MAIL_USERNAME = getenv('MAIL_USERNAME', 'viewly')
MAIL_PASSWORD = getenv('MAIL_PASSWORD', '')
MAIL_PORT = int(getenv('MAIL_PORT', 587))
MAIL_DEFAULT_SENDER = ('Viewly Alpha', 'support@view.ly')

# Flask-Security
SECURITY_TOKEN_MAX_AGE = 3600
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

# Logging
SENTRY_DSN = getenv('SENTRY_DSN')

# Disqus
DISQUS_PUBLIC_KEY = getenv('DISQUS_PUBLIC_KEY')
DISQUS_SECRET_KEY = getenv('DISQUS_SECRET_KEY')

# Ethereum chain
ETH_CHAIN = environ['ETH_CHAIN']
INFURA_KEY = environ['INFURA_KEY']

# Ethereum Contracts
VIEW_TOKEN_ADDRESS = environ['VIEW_TOKEN_ADDRESS']
VIDEO_PUBLISHER_ADDRESS = environ['VIDEO_PUBLISHER_ADDRESS']
VOTING_POWER_DELEGATOR_ADDRESS = environ['VOTING_POWER_DELEGATOR_ADDRESS']

VIEW_TOKEN_ABI = load_json_file(f'{config_folder_prefix()}/ViewToken.abi.json')
VIDEO_PUBLISHER_ABI = load_json_file(f'{config_folder_prefix()}/VideoPublisher.abi.json')
VOTING_POWER_DELEGATOR_ABI = load_json_file(
    f'{config_folder_prefix()}/VotingPowerDelegator.abi.json')

# Ethereum contract configuration / Governance
DISTRIBUTION_GAME_DAYS = getenv('DISTRIBUTION_GAME_DAYS', 7)
GAS_PRICE = int(getenv('GAS_PRICE', 20))  # in gwei

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
