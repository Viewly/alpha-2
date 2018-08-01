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

CHARSET = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

LEN = dict(
    video_id=12,
    channel_id=16,
    tx_id=66,
    eth_address=42,
)


def gen_uid():
    import uuid
    return str(uuid.uuid4()).replace('-', '')[::2]


def gen_video_id(length=LEN['video_id']):
    from random import sample
    return ''.join(sample(CHARSET, length))


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
    # id = db.Column(db.String(16), primary_key=True, default=gen_uid)
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


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    default_address = db.Column(db.String(LEN['eth_address']),
                                unique=True, index=True, nullable=False)
    data = db.Column(JSONB)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='wallets', lazy='dynamic')


class Channel(db.Model):
    id = db.Column(db.String(LEN['channel_id']),
                   unique=True, primary_key=True, default=gen_uid)

    # todo: add expression based index (lowercase, stripped, unique)
    slug = db.Column(db.String(32), unique=True)
    display_name = db.Column(db.String(32))
    description = db.Column(db.String(70))

    profile = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # relationships
    # -------------
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='channels')
    videos = db.relationship('Video', backref='channel')

    @declared_attr
    def __table_args__(self):
        return (
            db.Index(
                'ix_lc_unique_display_name',
                func.lower(self.display_name),
                unique=True),
        )


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.String(LEN['channel_id']),
                           db.ForeignKey('channel.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    @declared_attr
    def __table_args__(self):
        return (
            db.UniqueConstraint(
                'user_id',
                'channel_id',
                name='_follow_id',
            ),
        )


# -----------------
# VIDEOS
# -----------------

class TranscoderStatus(enum.Enum):
    pending = 0
    processing = 1
    complete = 2
    failed = 3


class Video(db.Model):
    id = db.Column(db.String(LEN['video_id']),
                   unique=True, primary_key=True, default=gen_video_id)
    # publish
    # -------
    title = db.Column(db.String(255))
    description = db.Column(db.UnicodeText)
    tags = db.Column(ARRAY(db.String, as_tuple=True, dimensions=1))
    license = db.Column(db.String(10))
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False)
    published_at = db.Column(db.DateTime(timezone=True))
    eth_address = db.Column(db.String(LEN['eth_address']))

    # inferred properties
    # -------------------
    analyzed_at = db.Column(db.DateTime(timezone=True))
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

    channel_id = db.Column(db.String(LEN['channel_id']), db.ForeignKey('channel.id'))

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
    timeline_file = db.Column(db.String(50))

    video_id = db.Column(db.String(LEN['video_id']),
                         db.ForeignKey('video.id'), nullable=False)


class TranscoderJob(db.Model):
    id = db.Column(db.String(20), unique=True, primary_key=True)
    status = db.Column(db.Enum(TranscoderStatus), nullable=False)
    preset_type = db.Column(db.String(20), nullable=False)
    video_id = db.Column(db.String(LEN['video_id']),
                         db.ForeignKey('video.id'), nullable=False)


class VideoFrameAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frame_id = db.Column(db.String(10))
    video_id = db.Column(db.String(LEN['video_id']))

    labels = db.Column(JSONB)
    nsfw_labels = db.Column(JSONB)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False)


class VideoPublisherEvents(db.Model):
    tx_id = db.Column(db.String(LEN['tx_id']), primary_key=True)
    video_id = db.Column(db.String(LEN['video_id']), unique=True, nullable=False)

    eth_address = db.Column(db.String(LEN['eth_address']), nullable=False)
    price = db.Column(db.Integer)
    block_num = db.Column(db.Integer, nullable=False)


# -----------------
# Distribution Game
# -----------------

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # unique pairs
    video_id = db.Column(db.String(LEN['video_id']),
                         db.ForeignKey('video.id'), nullable=False)
    eth_address = db.Column(db.String(LEN['eth_address']), nullable=False)

    # vote properties
    weight = db.Column(db.Integer, nullable=False)

    # signature
    ecc_message = db.Column(db.String(255), nullable=False)
    ecc_signature = db.Column(db.String(132), nullable=False)

    # derived properties (from blockchain)
    token_amount = db.Column(db.Integer)
    delegated_amount = db.Column(db.Integer)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    @declared_attr
    def __table_args__(self):
        return (
            db.UniqueConstraint(
                'video_id',
                'eth_address',
                name='_vote_id',
            ),
        )


class GamePeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=False)

    has_ended = db.Column(db.Boolean, nullable=False, default=False)

    # governance
    creator_rewards_pool = db.Column(db.Integer, nullable=False)
    voter_rewards_pool = db.Column(db.Integer, nullable=False)
    votes_per_user = db.Column(db.Integer, nullable=False)
    min_reward = db.Column(db.Integer, nullable=False)

    @declared_attr
    def __table_args__(self):
        return (
            db.UniqueConstraint(
                'start',
                'end',
                name='_period_id',
            ),
        )


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer,
                        db.ForeignKey('vote.id'), nullable=False, unique=True)
    video_id = db.Column(db.String(LEN['video_id']),
                         db.ForeignKey('video.id'), nullable=False)
    period_id = db.Column(db.Integer,
                          db.ForeignKey('game_period.id'), nullable=False)

    creator_reward = db.Column(db.DECIMAL(8, 3), nullable=False)  # 99,999.999 max
    voter_reward = db.Column(db.DECIMAL(8, 3), nullable=False)

    creator_payable = db.Column(db.Boolean, nullable=False)
    voter_payable = db.Column(db.Boolean, nullable=False)

    creator_txid = db.Column(db.String(LEN['tx_id']))
    voter_txid = db.Column(db.String(LEN['tx_id']))


class BalanceCache(db.Model):
    eth_address = db.Column(db.String(LEN['eth_address']), primary_key=True)
    balance = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)


class DelegationEvent(db.Model):
    tx_id = db.Column(db.String(LEN['tx_id']), primary_key=True)
    delegator = db.Column(db.String(LEN['eth_address']), nullable=False)
    beneficiary = db.Column(db.String(LEN['eth_address']), nullable=False)
    block_num = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)


# class ActiveDelegation(db.Model):
#     delegator = db.Column(db.String(LEN['video_id']), primary_key=True)
#     beneficiary = db.Column(db.String(LEN['eth_address']), index=True, nullable=False)
#
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False)
#     block_num = db.Column(db.Integer, nullable=False)
#     is_valid = db.Column(db.Boolean, nullable=False)
