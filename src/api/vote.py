import datetime as dt
import json

from flask_restful import (
    Resource,
    reqparse,
)
from marshmallow_sqlalchemy import ModelSchema

from .. import db
from ..config import DISTRIBUTION_GAME_DAYS
from ..core.eth import (
    is_valid_address,
    normalize_address,
    is_typed_signature_valid,
    is_same_address,
)
from ..core.utils import log_exception
from ..models import Vote, Video


class VoteSchema(ModelSchema):
    class Meta:
        model = Vote
        include_fk = True


vote_schema = VoteSchema()

parser = reqparse.RequestParser()
parser.add_argument('video_id', type=str, required=True)
parser.add_argument('eth_address', type=str, required=True)
parser.add_argument('weight', type=int)
parser.add_argument('ecc_message', type=str)
parser.add_argument('ecc_signature', type=str)


class VoteApi(Resource):
    def get(self):
        args = parser.parse_args()
        vote = db.session.query(Vote) \
            .filter(Vote.video_id == args['video_id'],
                    Vote.eth_address == args['eth_address']) \
            .first()
        return vote_schema.dump(vote).data or ({}, 404)

    def put(self):
        args = parser.parse_args()

        try:
            # validate that the video is published
            video = db.session.query(Video).filter_by(id=args['video_id']).one()
            assert video.published_at, 'Cannot vote on unpublished videos'
            # todo: when private videos are enabled, reject votes on them as well

            # validate that the video is within the distribution game age
            deadline = video.published_at.replace(tzinfo=None) + \
                       dt.timedelta(days=DISTRIBUTION_GAME_DAYS)
            assert deadline > dt.datetime.utcnow(), \
                'This video is no longer eligible for voting.'

            # validate ETH address, message integrity and the signature
            message, address = json.loads(args['ecc_message'])
            assert is_valid_address(address)
            assert is_same_address(address, args['eth_address'])
            vote = Vote(
                video_id=args['video_id'],
                weight=args['weight'],
                eth_address=normalize_address(address),
                ecc_message=json.dumps(message),
                ecc_signature=args['ecc_signature'],
                created_at=dt.datetime.utcnow(),
            )
            assert vote.video_id == message[0]['value']
            assert vote.weight == message[1]['value']
            assert 0 < vote.weight <= 100, f'Invalid Voting Weight of {vote.weight}'
            t1, t2 = sorted([
                dt.datetime.utcnow(),
                dt.datetime.utcfromtimestamp(message[2]['value']),
            ])
            timestamp_delta = (t2 - t1).seconds
            assert abs(timestamp_delta) < 600, \
                'Timestamp is more than 10 minutes out of sync with UTC'
            assert is_typed_signature_valid(
                message, vote.ecc_signature, vote.eth_address)

            db.session.add(vote)
            db.session.commit()
        except AssertionError as e:
            log_exception()
            return dict(message=str(e)), 400
        except Exception as e:
            log_exception()
            return dict(message=str(e)), 500

        return vote_schema.dump(vote).data
