from flask_security import (
    UserMixin,
    RoleMixin,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from . import db
from .utils import gen_uid, gen_video_id

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


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

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    channels = db.relationship('Channel', back_populates='user')
    uploads = db.relationship('Upload', back_populates='user')


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

    # todo: add searchable index
    title = db.Column(db.String(255))
    description = db.Column(db.String(1000))
    tags = db.Column(ARRAY(db.String, as_tuple=True, dimensions=1))

    # inferred properties
    # -------------------
    language = db.Column(db.String(2))
    is_nsfw = db.Column(db.Boolean)

    # dynamic properties
    # ------------------
    video_metadata = db.Column(JSONB)
    stats = db.Column(JSONB)

    # relationships
    # -------------
    channel_id = db.Column(db.String(16), db.ForeignKey('channel.id'))


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # relationships
    # -------------
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='uploads')
