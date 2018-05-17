import datetime as dt
import random

from celery.schedules import crontab
from eth_utils import from_wei
from funcy import (
    partial,
    rpartial,
    compose,
    chunks,
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
    is_video_published,
    view_token_balance,
    get_infura_web3,
    find_block_from_timestamp,
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

    def is_published(video_id):
        return is_video_published(video_id), video_id

    publish_results = lkeep(thread_multi(
        fn=is_published,
        fn_args=[None],
        dep_args=[video.id for video in unpublished_videos],
        max_workers=10,
        re_raise_errors=False,
    ))

    for status, video_id in publish_results:
        if status:
            video = session.query(Video).filter_by(id=video_id).one()
            video.published_at = dt.datetime.utcnow()
            session.add(video)

    session.commit()


@cron.task(ignore_result=True)
def evaluate_votes():
    """
    Evaluate token balances of the voter for the past 7 days.

    The purpose of this method is to prevent abuse caused by
    people who are voting and moving their tokens in an attempt to
    be able to vote again.

    The evaluation will pick random blocks in the average of 1
    block per hour, and acknowledge the minimum balance during
    this period as the voting power.
    """
    days = DISTRIBUTION_GAME_DAYS

    session = db_session()
    pending_votes = session.query(Vote).filter(Vote.token_amount.is_(None))

    w3 = get_infura_web3()

    for vote in pending_votes:
        review_period_end = int(vote.created_at.timestamp())
        review_period_start = int((vote.created_at - dt.timedelta(days=days)).timestamp())

        find_block = partial(find_block_from_timestamp, w3)
        review_block_range = [find_block(x).number for x in
                              (review_period_start, review_period_end)]

        # get random VIEW balances on the voter's address for the last 7 days
        # split search range into chunks that contain ~ 1 hour worth of blocks
        chunk_size = (review_block_range[1] - review_block_range[0]) // (days * 24)
        balances = map(
            lambda block_num: view_token_balance(vote.eth_address, block_num=block_num),
            (random.randrange(*chunk_range) for chunk_range in
             chunks(chunk_size, review_block_range))
        )

        to_eth = compose(int, rpartial(from_wei, 'ether'))
        min_balance = min(to_eth(x) for x in balances)

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
