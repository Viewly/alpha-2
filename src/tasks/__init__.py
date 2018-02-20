from celery import Celery

from ..config import (
    CELERY_BACKEND_URL,
    CELERY_BROKER_URL,
    SQLALCHEMY_DATABASE_URI,
    SENTRY_DSN,
)


def new_celery(worker_name: str, **kwargs):
    if SENTRY_DSN:
        init_sentry()

    return Celery(
        worker_name,
        backend=CELERY_BACKEND_URL,
        broker=CELERY_BROKER_URL,
        **kwargs
    )


def init_sentry():
    """ Inject Sentry logging into Celery."""
    from raven import Client
    from raven.contrib.celery import register_signal, register_logger_signal
    import logging

    client = Client()
    register_logger_signal(client, loglevel=logging.ERROR)
    register_signal(client, ignore_expected=True)


def db_session(**kwargs):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    return \
        scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine,
                         **kwargs))
