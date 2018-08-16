from flask_restful import (
    Resource,
)

from ..core.eth import gas_price


class GasPriceApi(Resource):
    def get(self):
        price = gas_price()
        return {'normal': price - 4, 'fast': price}
