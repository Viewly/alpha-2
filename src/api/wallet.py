import datetime as dt
import json

from eth_utils import to_checksum_address
from flask_restful import (
    Resource,
    reqparse,
)
from flask_security import current_user
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import desc

from .utils import auth_required
from .. import db
from ..models import Wallet


class WalletSchema(ModelSchema):
    class Meta:
        model = Wallet


wallet_schema = WalletSchema()

parser = reqparse.RequestParser()
parser.add_argument('data', required=True)


class WalletApi(Resource):
    method_decorators = [auth_required]

    def get(self):
        wallet = \
            (db.session.query(Wallet)
             .filter(Wallet.user_id == current_user.id)
             .order_by(desc(Wallet.id))
             .first())
        return wallet_schema.dump(wallet).data or ({}, 404)

    def put(self):
        args = parser.parse_args()
        data = json.loads(args['data'])
        default_address = to_checksum_address(data['address'])

        wallet = db.session.query(Wallet).filter_by(
            user_id=current_user.id,
            default_address=default_address,
        ).first()

        if not wallet:
            wallet = Wallet(
                user_id=current_user.id,
                data=data,
                default_address=default_address,
                created_at=dt.datetime.utcnow(),
            )

            db.session.add(wallet)
            db.session.commit()
        return wallet_schema.dump(wallet).data
