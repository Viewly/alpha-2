from flask_security import (
    UserMixin,
    RoleMixin,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    ARRAY,
)

from . import db
from .utils import gen_uid, gen_video_id

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    # id = db.Column(db.String(16), primary_key=True, default=generate_uid)
    id = db.Column(db.Integer, primary_key=True)

    # authentication
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    # traceable
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    # temporary fields
    can_upload = db.Column(db.Boolean, default=True)

    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'),
    )
    channels = db.relationship('Channel', back_populates='user')
    videos = db.relationship('Video', back_populates='user', lazy='dynamic')


class Channel(db.Model):
    id = db.Column(db.String(16), unique=True, primary_key=True, default=gen_uid())

    # todo: add expression based index (lowercase, stripped, unique)
    slug = db.Column(db.String(32), unique=True)
    display_name = db.Column(db.String(32))

    profile = db.Column(JSONB)

    # relationships
    # -------------
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='channels')
    videos = db.relationship('Video', backref='channel')


class Video(db.Model):
    id = db.Column(db.String(12), unique=True, primary_key=True, default=gen_video_id())

    # uploader
    # --------
    s3_bucket_name = db.Column(db.String(50), nullable=False)
    s3_input_key = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # transcoder
    # --------
    transcoder_pipeline = db.Column(db.String(30))
    transcoder_job_id = db.Column(db.String(30))
    # transcoder_status =  enum(pending, in_progress, failed, succeeded)
    # transcoder_s3_path = "bucket_name:/v1/user_id/channel_id/video_id"

    # publish
    # -------
    # todo: these fields should be searchable (indexed)
    title = db.Column(db.String(255))
    description = db.Column(db.String(1000))
    tags = db.Column(ARRAY(db.String, as_tuple=True, dimensions=1))
    license = db.Column(db.String(10))
    published_at = db.Column(db.DateTime(timezone=True))

    # inferred properties
    # -------------------
    language = db.Column(db.String(2))
    is_nsfw = db.Column(db.Boolean)  # or integer for confidence

    # dynamic properties
    # ------------------
    video_metadata = db.Column(JSONB)
    stats = db.Column(JSONB)

    # relationships
    # -------------
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='videos')

    channel_id = db.Column(db.String(16), db.ForeignKey('channel.id'))
