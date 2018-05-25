from os import getenv

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
from raven.contrib.flask import Sentry
from sassutils.wsgi import SassMiddleware

from .config import IS_PRODUCTION

# Initialize Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_pyfile('config.py')

# Initialize Flask Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Optionally initialize Sentry (error logging)
sentry = Sentry(app) if getenv('SENTRY_DSN') else None

# Markdown Support
md_features = ['autolink', 'fenced_code', 'underline', 'highlight', 'quote',
               'math', 'superscript', 'tables', 'wrap',
               'no_html', 'smartypants']
md_features = {x: True for x in md_features}
Misaka(app, **md_features)

from . import models

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)

# Register Blueprints
from .b_channel import channel as channel_blueprint
from .b_game import game as game_blueprint
from .b_upload import upload as upload_blueprint
from .api import blueprint as api_blueprint

app.register_blueprint(upload_blueprint, url_prefix='/upload')
app.register_blueprint(channel_blueprint, url_prefix='/channel')
app.register_blueprint(game_blueprint, url_prefix='/game')
app.register_blueprint(api_blueprint, url_prefix='/api')


# Developer Helper Commands
# -------------------------
@app.cli.command('db-init')
def init_db():
    """ Initialize the database """
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1]
    db_exists = delegator.run(f'psql -lqt | cut -d \| -f 1 | grep -qw {db_name}').out
    if db_exists:
        print(f'Database "{db_name}" already exists. '
              f'Perhaps you may want to run `db-reset` instead.')
    else:
        delegator.run(f'createdb {db_name}')
        db.create_all()
        print(f'Database "{db_name}" Initialized.')


@app.cli.command('db-reset')
def reset_db():
    """ Re-initialize the database.

    This will only work if no active connections are open (ie. Flask Server).
    """
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1]
    delegator.run(f'dropdb --if-exists {db_name}')
    delegator.run(f'createdb {db_name}')
    db.create_all()
    print(f'Database "{db_name}" has been reset.')


# Initialize scss compilation in development
if not IS_PRODUCTION:
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'src': ('static/scss', 'static/css/compiled', '/static/css/compiled')
    })
