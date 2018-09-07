from flask_restful import (
    Resource,
    reqparse,
)
from flask import url_for
from sqlalchemy import func

from .. import db
from ..models import Channel
from ..methods import guess_avatar_cdn_url

parser = reqparse.RequestParser()
parser.add_argument('q', type=str, required=True)
parser.add_argument('limit', type=int)

class FindChannelApi(Resource):
    def get(self):
        try:
            args = parser.parse_args()
            q = args['q'].replace('"', '').replace("'", '')
            assert len(q) >= 3, 'Search query too short'
            limit = args['limit'] or 10
            assert 0 < limit <= 25, 'Results limit should be between 1 and 25 inclusive.'
            channels = \
                (db.session.query(Channel)
                .filter(Channel.display_name.ilike(f"%{q}%"))
                .limit(limit)
                .all())
            return [{
                'channel_id': x.id,
                'channel_url': url_for('view_channel', channel_id=x.id, _external=True),
                'display_name': x.display_name,
                'avatar_url': guess_avatar_cdn_url(x.id, 'tiny'),
            } for x in channels]
        except AssertionError as e:
            return dict(message=str(e)), 400
