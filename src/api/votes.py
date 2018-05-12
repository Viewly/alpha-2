from flask_restful import (
    Resource,
    reqparse,
    fields,
    marshal,
)
from sqlalchemy import or_

from .. import db
from ..models import Vote

parser = reqparse.RequestParser()
parser.add_argument('video_id', type=str, required=True)

output_fields = {
    'weight': fields.Integer,
    'token_amount': fields.Integer,
    'voter_address': fields.String(attribute='eth_address'),
    'created_at': fields.DateTime,
}


class VotesApi(Resource):
    def get(self):
        args = parser.parse_args()
        votes = db.session.query(Vote) \
            .filter(Vote.video_id == args['video_id'],
                    or_(Vote.token_amount > 0,
                        Vote.delegated_amount > 0)) \
            .all()

        return {
            'video_id': args['video_id'],
            'count': len(votes),
            'stake': sum([x.token_amount + x.delegated_amount for x in votes]),
            'votes': marshal(votes, output_fields)
        }
