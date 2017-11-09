from celery import Celery

from .. import app


def new_celery(worker_name: str, **kwargs):
    return Celery(
        worker_name,
        backend=app.config['CELERY_BACKEND_URL'],
        broker=app.config['CELERY_BROKER_URL'],
        **kwargs
    )
