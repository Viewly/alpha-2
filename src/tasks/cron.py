import datetime as dt

from celery.schedules import crontab
from funcy import (
    lkeep,
)

from . import (
    new_celery,
    db_session,
)
from .analyze import extract_labels_from_video
from .shared import generate_manifest_file
from .transcoder import transcoder_post_processing
from ..config import (
    DISTRIBUTION_GAME_DAYS,
)
from ..core.et import get_job_status
from ..core.eth import (
    get_publisher_address,
    null_address,
    confirmed_block_num,
    min_stake_for_period,
)
from ..core.utils import thread_multi
from ..models import (
    Video,
    Vote,
    TranscoderStatus,
    TranscoderJob,
)

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
        'schedule': crontab(minute='*/2'),
        'args': ()
    },
    'evaluate-votes': {
        'task': 'src.tasks.cron.evaluate_votes',
        'schedule': crontab(minute='*/2'),
        'args': ()
    },
    'retry-label-extraction': {
        'task': 'src.tasks.cron.retry_label_extraction',
        'schedule': crontab(hour='*/2'),  # every 2 hours
        'args': ()
    },
}


@cron.task(ignore_result=True)
def refresh_transcoder_jobs():
    session = db_session()
    unfinished_jobs = \
        session.query(TranscoderJob).filter_by(
            status=TranscoderStatus.processing
        )

    status_map = {
        "Complete": TranscoderStatus.complete,
        "Submitted": TranscoderStatus.processing,
        "Progressing": TranscoderStatus.processing,
        "Error": TranscoderStatus.failed,
    }

    for job in unfinished_jobs:
        status = get_job_status(job.id)
        job.status = status_map[status]
        if job.status == TranscoderStatus.complete:
            generate_manifest_file.delay(job.video_id)
            transcoder_post_processing.delay(job.video_id, job.id)
        session.add(job)
        session.commit()


@cron.task(ignore_result=True)
def refresh_unpublished_videos():
    session = db_session()
    unpublished_videos = \
        session.query(Video).filter(
            Video.channel_id.isnot(None),
            Video.published_at.is_(None)
        )

    trusted_block_num = confirmed_block_num(5)

    def is_published(video_id):
        addr = get_publisher_address(video_id, trusted_block_num)
        return addr, video_id

    publish_results = lkeep(thread_multi(
        fn=is_published,
        fn_args=[None],
        dep_args=[video.id for video in unpublished_videos],
        max_workers=10,
        re_raise_errors=False,
    ))

    for publisher_addr, video_id in publish_results:
        if publisher_addr != null_address:
            video = session.query(Video).filter_by(id=video_id).one()
            video.published_at = dt.datetime.utcnow()
            video.eth_address = publisher_addr
            session.add(video)

    session.commit()


@cron.task(ignore_result=True)
def evaluate_votes():
    """
    Evaluate token balances of the voter for the past 7 days.
    Check for delegations, and delegation amounts.
    """
    session = db_session()
    pending_votes = session.query(Vote).filter(Vote.token_amount.is_(None))

    for vote in pending_votes:
        min_balance = min_stake_for_period(
            vote.eth_address,
            vote.created_at,
            lookback_days=DISTRIBUTION_GAME_DAYS,
        )

        vote.token_amount = min_balance
        vote.delegated_amount = 0  # todo: implement delegation contract
        session.add(vote)
        session.commit()


@cron.task(ignore_result=True)
def retry_label_extraction():
    videos = db_session().query(Video).filter(
        Video.published_at.isnot(None),
        Video.analyzed_at.is_(None))

    for video in videos:
        extract_labels_from_video.delay(video.id)
