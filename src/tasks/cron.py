from celery.schedules import crontab

from . import (
    new_celery,
    db_session,
)
from .et import get_job_status
from ..models import Video, TranscoderStatus

cron = new_celery(
    'cron-tasks',
    include=['src.tasks.cron'],
)
cron.conf.update(
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)

cron.conf.beat_schedule = {
    'refresh-transcoder-jobs': {
        'task': 'src.tasks.cron.refresh_transcoder_jobs',
        'schedule': crontab(minute='*/2'),
        'args': ()
    },
}


@cron.task(ignore_result=True)
def refresh_transcoder_jobs():
    session = db_session()
    unfinished_jobs = \
        session.query(Video).filter(
            Video.transcoder_job_id is not None,
            Video.transcoder_status != TranscoderStatus.complete)

    status_map = {
        "Complete": TranscoderStatus.complete,
        "Submitted": TranscoderStatus.processing,
        "Progressing": TranscoderStatus.processing,
        "Error": TranscoderStatus.failed,
    }

    for video in unfinished_jobs:
        status = get_job_status(video.transcoder_job_id)
        video.transcoder_status = status_map[status]
        session.add(video)

    session.commit()
