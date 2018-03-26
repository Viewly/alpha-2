from flask import Blueprint
from flask_restful import (
    Api,
)

from .vote import VoteApi
from .follow import FollowApi

blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_resource(VoteApi, '/vote')
api.add_resource(FollowApi, '/follow')
