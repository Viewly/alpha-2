from flask_security import current_user
from funcy import decorator
from flask_restful import abort


@decorator
def auth_required(fn):
    if not current_user.is_authenticated:
        abort(401)
    return fn()
