from flask import Blueprint
from flask_restful import (
    Api,
)

from .follow import FollowApi
from .rewards import RewardsApi
from .vote import VoteApi
from .votes import VotesApi
from .wallet import WalletApi

blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_resource(VoteApi, '/vote')
api.add_resource(VotesApi, '/votes')
api.add_resource(FollowApi, '/follow')
api.add_resource(RewardsApi, '/rewards')
api.add_resource(WalletApi, '/wallet')
