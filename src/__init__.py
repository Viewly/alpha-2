import os

import delegator
from flask import (
    Flask,
)
from flask_mail import Mail
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'not_a_good_secret')
app.config['VIRTUAL_HOST'] = os.getenv('VIRTUAL_HOST', 'localhost:5000')
app.config['IPFS_GATEWAY'] = os.getenv('IPFS_GATEWAY', 'http://localhost:8080')
app.config['UPLOADER_URI'] = os.getenv('UPLOADER_URI', 'http://localhost:5005')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_URI', 'postgres://localhost/viewly_beta')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 50
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 200
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'postmaster@mg.view.ly')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '18e7f9181eeb08de7de059ae659e07c0')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.mailgun.org')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 2525))
app.config['MAIL_DEFAULT_SENDER'] = ('Viewly Alpha', 'alpha@view.ly')
mail = Mail(app)

# Flask-Security
app.config['SECURITY_PASSWORD_SALT'] = ""
app.config['SECURITY_CONFIRMABLE'] = bool(os.getenv('PRODUCTION'))
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORDLESS'] = False
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_EMAIL_SUBJECT_REGISTER'] = "Welcome to Viewly. Please confirm your email."

# Markdown Support
md_features = ['autolink', 'fenced_code', 'underline', 'highlight', 'quote',
               'math', 'superscript', 'tables', 'wrap',
               'no_html', 'smartypants']
md_features = {x: True for x in md_features}
Misaka(app, **md_features)

# workaround flask issue #1907
if not os.getenv('PRODUCTION'):
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}

from . import models

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)

# Register Blueprints
from .b_upload import upload as upload_blueprint

app.register_blueprint(upload_blueprint, url_prefix='/upload/')


# Developer Helper Commands
# -------------------------
@app.cli.command('db-init')
def init_db():
    """ Initialize the database """
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1]
    db_exists = delegator.run(f'psql -lqt | cut -d \| -f 1 | grep -qw {db_name}').out
    if db_exists:
        print(f'Database {db_name} already exists. '
              f'Perhaps you may want to run `db-reset` instead.')
    else:
        delegator.run(f'createdb {db_name}')
        db.create_all()
        print(f'Database {db_name} Initialized.')


@app.cli.command('db-reset')
def reset_db():
    """ Re-initialize the database.

    This will only work if no active connections are open (ie. Flask Server).
    """
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1]
    delegator.run(f'dropdb --if-exists {db_name}')
    delegator.run(f'createdb {db_name}')
    db.create_all()
    print(f'Database {db_name} has been reset.')
