from flask_restful import (
    Resource,
    reqparse,
    fields,
    marshal,
)
from sqlalchemy import func

from .. import db
from ..models import Reward

parser = reqparse.RequestParser()
parser.add_argument('video_id', type=str, required=True)

output_fields = {
    'video_id': fields.String,
    'count': fields.Integer,
    'creator_rewards': fields.Float,
    'voter_rewards': fields.Float,
}


class RewardsApi(Resource):
    def get(self):
        args = parser.parse_args()
        summary = \
            (db.session.query(
                func.count(Reward.id).label('rewards_count'),
                func.sum(Reward.creator_reward).label('creator_rewards'),
                func.sum(Reward.voter_reward).label('voter_rewards'))
             .filter_by(video_id=args['video_id'], creator_payable=True)
             .one())

        return marshal(
            {
                'video_id': args['video_id'],
                'count': summary.rewards_count,
                'creator_rewards': summary.creator_rewards,
                'voter_rewards': summary.voter_rewards,
            },
            output_fields
        )
