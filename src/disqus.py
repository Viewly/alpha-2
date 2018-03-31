import base64
import hashlib
import hmac
import json
import time
from typing import Union

from flask import url_for
from flask_security import current_user
from funcy import some

from .config import (
    DISQUS_PUBLIC_KEY,
    DISQUS_SECRET_KEY,
)
from .methods import guess_avatar_cdn_url
from .models import (
    db,
    Channel,
    User,
)


def to_disqus_user(obj: Union[Channel, User]):
    """ Convert Viewly User or Channel into a unique Disqus user."""
    if isinstance(obj, Channel):
        return dict(
            id=obj.id,
            username=obj.display_name,
            email=obj.user.email,
            url=url_for('view_channel', channel_id=obj.id, _external=True),
            avatar=guess_avatar_cdn_url(obj.id, 'tiny')  # todo, avatar db lookup
        )
    elif isinstance(obj, User):
        return dict(
            id=f'Anon-{obj.id}',
            username=f'Anon-{obj.id}',
            email=obj.email,
            avatar='https://i.imgur.com/32AwiVw.jpg',
        )


def get_disqus_user(preferred_channel_id=None):
    """ If user is logged in, generate an appropriate Disqus user:
      - Same channel as preferred channel if available (for OP)
      - First channel user has
      - Anon account if user has no channels
      - None if not logged in
    """
    if current_user and current_user.is_authenticated:
        channels = db.session.query(Channel).filter_by(user_id=current_user.id).all()
        preferred_channel = some(lambda x: x.id == preferred_channel_id, channels)
        if preferred_channel:
            return to_disqus_user(preferred_channel)
        elif channels:
            return to_disqus_user(channels[0])
        else:
            user = db.session.query(User).filter_by(id=current_user.id).one()
            return to_disqus_user(user)


def get_disqus_sso(user):
    if not user:
        return ''

    data = json.dumps(user)
    message = base64.b64encode(bytes(data, 'utf-8')).decode('utf-8')
    timestamp = int(time.time())
    sig = hmac.HMAC(
        bytes(DISQUS_SECRET_KEY, 'utf-8'),
        bytes(f'{message} {timestamp}', 'utf-8'),
        hashlib.sha1).hexdigest()

    return """
        this.page.remote_auth_s3 = "%(message)s %(sig)s %(timestamp)s";
        this.page.api_key = "%(pub_key)s";""" % dict(
        message=message,
        timestamp=timestamp,
        sig=sig,
        pub_key=DISQUS_PUBLIC_KEY,
    )
