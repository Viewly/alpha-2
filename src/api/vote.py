import datetime as dt

from flask_restful import (
    Resource,
    reqparse,
)
from marshmallow_sqlalchemy import ModelSchema

from .. import db
from ..core.eth import (
    is_valid_address,
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
parser.add_argument('ecc_message', type=str)
parser.add_argument('ecc_signature', type=str)


class VoteApi(Resource):
    def get(self):
        args = parser.parse_args()
        vote = db.session.query(Vote) \
            .filter(Vote.video_id == args['video_id'],
                    Vote.eth_address == args['eth_address']) \
            .first()
        return vote or ({}, 404)

    def put(self):
        args = parser.parse_args()
        vote = Vote(
            video_id=args['video_id'],
            eth_address=args['eth_address'],
            ecc_message=args['ecc_message'],
            ecc_signature=args['ecc_signature'],
            created_at=dt.datetime.utcnow(),
        )

        # validate ETH address and the signature
        try:
            assert is_valid_address(vote.eth_address)
            # assert is_valid_signature(
            #     vote.ecc_message, vote.ecc_signature, vote.eth_address)
        except Exception as e:
            return dict(message=str(e)), 500

        db.session.add(vote)
        db.session.commit()
        return vote_schema.dump(vote)
