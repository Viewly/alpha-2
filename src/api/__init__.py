from flask import Blueprint
from flask_restful import (
    Api,
)

from .vote import VoteApi

blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_resource(VoteApi, '/vote')
