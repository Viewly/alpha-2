import enum

from flask_security import (
    UserMixin,
    RoleMixin,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    ARRAY,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import coalesce

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
    confirmed_at = db.Column(db.DateTime)

    # traceable
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
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
    id = db.Column(db.String(16), unique=True, primary_key=True, default=gen_uid)

    # todo: add expression based index (lowercase, stripped, unique)
    slug = db.Column(db.String(32), unique=True)
    display_name = db.Column(db.String(32))

    profile = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # relationships
    # -------------
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='channels')
    videos = db.relationship('Video', backref='channel')


class TranscoderStatus(enum.Enum):
    pending = 0
    processing = 1
    complete = 2
    failed = 3


class Video(db.Model):
    id = db.Column(db.String(12), unique=True, primary_key=True, default=gen_video_id)

    # publish
    # -------
    title = db.Column(db.String(255))
    description = db.Column(db.UnicodeText)
    tags = db.Column(ARRAY(db.String, as_tuple=True, dimensions=1))
    license = db.Column(db.String(10))
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False)
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

    file_mapper = db.relationship(
        "FileMapper",
        uselist=False,
        cascade="all, delete-orphan",
        backref="video",
    )

    channel_id = db.Column(db.String(16), db.ForeignKey('channel.id'))

    @declared_attr
    def __table_args__(self):
        return (
            db.Index('idx_tsv_title',
                     func.to_tsvector("english", self.title),
                     postgresql_using="gin"),
            db.Index('idx_tsv_title_description',
                     func.to_tsvector(
                         "english",
                         self.title + ' ' + coalesce(self.description, '')),
                     postgresql_using="gin"),
        )


class FileMapper(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # where was video/thumbnail uploaded to
    s3_upload_bucket = db.Column(db.String(50))
    s3_upload_video_key = db.Column(db.String(50))
    s3_upload_thumbnail_key = db.Column(db.String(50))

    # s3_thumbnails_path = db.Column(db.String(50))
    video_formats = db.Column(JSONB)
    thumbnail_files = db.Column(JSONB)  # thumbnail_formats

    video_id = db.Column(db.String(12), db.ForeignKey('video.id'), nullable=False)


class TranscoderJob(db.Model):
    id = db.Column(db.String(20), unique=True, primary_key=True)
    status = db.Column(db.Enum(TranscoderStatus), nullable=False)
    preset_type = db.Column(db.String(20), nullable=False)
    video_id = db.Column(db.String(12), db.ForeignKey('video.id'), nullable=False)
