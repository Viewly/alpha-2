import datetime as dt

from celery.schedules import crontab

from ..core.eth import is_video_published
from . import (
    new_celery,
    db_session,
)
from ..core.et import get_job_status
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
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'refresh-unpublished-videos': {
        'task': 'src.tasks.cron.refresh_unpublished_videos',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
}


@cron.task(ignore_result=True)
def refresh_transcoder_jobs():
    session = db_session()
    unfinished_jobs = \
        session.query(Video).filter(
            Video.transcoder_job_id is not None,
            Video.transcoder_status != TranscoderStatus.complete,
            Video.transcoder_status != TranscoderStatus.failed,
        )

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


@cron.task(ignore_result=True)
def refresh_unpublished_videos():
    session = db_session()
    unpublished_videos = \
        session.query(Video).filter(
            Video.channel_id is not None,
            Video.published_at == None
        )

    for video in unpublished_videos:
        if is_video_published(video.id):
            video.published_at = dt.datetime.utcnow()
            session.add(video)

    session.commit()
