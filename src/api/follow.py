import datetime as dt

from flask_restful import (
    Resource,
    reqparse,
)
from flask_security import current_user
from marshmallow_sqlalchemy import ModelSchema

from .utils import auth_required
from .. import db
from ..models import Follow


class FollowSchema(ModelSchema):
    class Meta:
        model = Follow
        include_fk = True


follow_schema = FollowSchema()

parser = reqparse.RequestParser()
parser.add_argument('channel_id', type=str, required=True)


class FollowApi(Resource):
    method_decorators = [auth_required]

    def get(self):
        args = parser.parse_args()
        follow = db.session.query(Follow) \
            .filter(Follow.user_id == current_user.id,
                    Follow.channel_id == args['channel_id']) \
            .first()
        return follow_schema.dump(follow).data or ({}, 404)

    def put(self):
        args = parser.parse_args()
        follow = Follow(
            user_id=current_user.id,
            channel_id=args['channel_id'],
            created_at=dt.datetime.utcnow(),
        )

        db.session.add(follow)
        db.session.commit()
        return follow_schema.dump(follow).data

    def delete(self):
        args = parser.parse_args()
        follow = db.session.query(Follow) \
            .filter(Follow.user_id == current_user.id,
                    Follow.channel_id == args['channel_id']) \
            .one()
        db.session.delete(follow)
        db.session.commit()

        return {}, 200
