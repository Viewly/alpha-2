from celery import Celery

from ..config import (
    CELERY_BACKEND_URL,
    CELERY_BROKER_URL,
    SQLALCHEMY_DATABASE_URI,
)


def new_celery(worker_name: str, **kwargs):
    return Celery(
        worker_name,
        backend=CELERY_BACKEND_URL,
        broker=CELERY_BROKER_URL,
        **kwargs
    )


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
