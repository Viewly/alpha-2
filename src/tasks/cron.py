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
    min_balance_for_period,
    get_beneficiary_address,
    validate_beneficiary,
    to_checksum_address,
)
from ..core.utils import thread_multi
from ..models import (
    Video,
    Vote,
    TranscoderStatus,
    TranscoderJob,
    BalanceCache,
    DelegationEvent,
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

    def active_delegations(beneficiary_addr: str):
        beneficiary_addr = to_checksum_address(beneficiary_addr)
        a_week_ago = dt.datetime.utcnow() - dt.timedelta(days=7)
        delegations = \
            (session.query(DelegationEvent)
             .filter(DelegationEvent.beneficiary == beneficiary_addr,
                     DelegationEvent.created_at < a_week_ago)
             .all())

        return [x for x in delegations
                if validate_beneficiary(x.delegator, x.beneficiary)]

    for vote in pending_votes:
        # get voters balance
        if get_beneficiary_address(vote.eth_address):
            vote.token_amount = 0
        else:
            vote.token_amount = refresh_balance(
                vote.eth_address,
                vote.created_at,
                lookback_days=DISTRIBUTION_GAME_DAYS
            ).balance

        # get voters delegations
        vote.delegated_amount = sum([
            refresh_balance(
                x.delegator,
                vote.created_at,
                lookback_days=DISTRIBUTION_GAME_DAYS
            ).balance for x in active_delegations(vote.eth_address)
        ])
        session.add(vote)
        session.commit()


def refresh_balance(eth_address: str,
                    created_at: dt.datetime,
                    lookback_days: int = 7):
    session = db_session()
    an_hour_ago = dt.datetime.utcnow() - dt.timedelta(hours=1)
    balance = \
        (session.query(BalanceCache)
         .filter(BalanceCache.eth_address == eth_address,
                 BalanceCache.updated_at > an_hour_ago)
         .first())
    if not balance:
        min_balance = min_balance_for_period(
            eth_address,
            created_at,
            lookback_days=lookback_days,
        )
        balance = BalanceCache(
            eth_address=eth_address,
            balance=min_balance,
            updated_at=dt.datetime.utcnow()
        )
        session.merge(balance)
        session.commit()
    return balance


@cron.task(ignore_result=True)
def retry_label_extraction():
    videos = db_session().query(Video).filter(
        Video.published_at.isnot(None),
        Video.analyzed_at.is_(None))

    for video in videos:
        extract_labels_from_video.delay(video.id)
