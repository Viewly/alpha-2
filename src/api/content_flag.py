import datetime as dt
import json

from flask_restful import (
    Resource,
    reqparse,
)
from flask_security import current_user
from marshmallow_sqlalchemy import ModelSchema

from .utils import auth_required

from .. import db
from ..core.utils import log_exception
from ..models import ContentFlag


class FlagSchema(ModelSchema):
    class Meta:
        model = ContentFlag
        include_fk = True


flag_schema = FlagSchema()

parser = reqparse.RequestParser()
parser.add_argument('video_id', type=str, required=True)
parser.add_argument('flag_type', type=str)


class FlagApi(Resource):
    method_decorators = [auth_required]

    def get(self):
        args = parser.parse_args()
        flag = \
            (db.session.query(ContentFlag)
             .filter(ContentFlag.video_id == args['video_id'],
                     ContentFlag.user_id == current_user.id)
             .first())
        return flag_schema.dump(flag).data or ({}, 404)

    def put(self):
        args = parser.parse_args()
        try:
            assert args['flag_type'] in \
                ['xxx', 'hate', 'scam', 'spam', 'plagiarism'], 'Invalid flag'

            flag = ContentFlag(
                user_id=current_user.id,
                video_id=args['video_id'],
                flag_type=args['flag_type'],
                created_at=dt.datetime.utcnow(),
            )
            db.session.add(flag)
            db.session.commit()
        except AssertionError as e:
            log_exception()
            return dict(message=str(e)), 400
        except Exception as e:
            log_exception()
            return dict(message=str(e)), 500

        return flag_schema.dump(flag).data
