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
        vote = Vote(
            video_id=args['video_id'],
            weight=args['weight'],
            eth_address=args['eth_address'],
            ecc_message=args['ecc_message'],
            ecc_signature=args['ecc_signature'],
            created_at=dt.datetime.utcnow(),
        )

        # validate ETH address, signed message and the signature
        try:
            assert is_valid_address(vote.eth_address)
            vote.eth_address = normalize_address(vote.eth_address)

            message, addr = json.loads(vote.ecc_message)
            assert vote.eth_address == normalize_address(addr)
            assert vote.video_id == message[0].get('value')
            assert vote.weight == message[1].get('value')
            assert 0 > vote.weight <= 100, f'Invalid Voting Weight of {vote.weight}'

            # assert is_valid_signature(
            #     vote.ecc_message, vote.ecc_signature, vote.eth_address)
        except Exception as e:
            return dict(message=str(e)), 500

        db.session.add(vote)
        db.session.commit()
        return vote_schema.dump(vote).data
