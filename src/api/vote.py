import datetime as dt
import json

from flask_restful import (
    Resource,
    reqparse,
)
from marshmallow_sqlalchemy import ModelSchema

from .. import db
from ..core.eth import (
    is_valid_address,
    normalize_address,
    is_typed_signature_valid,
    is_same_address,
)
from ..models import Vote


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

        # validate ETH address, message integrity and the signature
        try:
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
            timestamp_delta = \
                (dt.datetime.utcnow() -
                 dt.datetime.utcfromtimestamp(message[2]['value'])).seconds
            assert 0 <= timestamp_delta < 3600, 'Vote is older than 1 hour'
            assert is_typed_signature_valid(
                message, vote.ecc_signature, vote.eth_address)
        except Exception as e:
            # todo, log exception to sentry
            return dict(message=str(e)), 500

        db.session.add(vote)
        db.session.commit()
        return vote_schema.dump(vote).data
