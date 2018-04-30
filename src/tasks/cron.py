import datetime as dt
import random
from collections import Counter

from celery.schedules import crontab
from eth_utils import from_wei
from funcy import (
    partial,
    rpartial,
    compose,
    chunks,
)
from sqlalchemy import asc

from . import (
    new_celery,
    db_session,
)
from .shared import generate_manifest_file
from .transcoder import transcoder_post_processing
from ..config import (
    DISTRIBUTION_GAME_DAYS,
    S3_VIDEOS_BUCKET,
)
from ..core.et import get_job_status
from ..core.eth import (
    is_video_published,
    view_token_balance,
    get_infura_web3,
    find_block_from_timestamp,
)
from ..core.rkg import Rekognition
from ..core.s3 import S3Transfer
from ..models import (
    Video,
    Vote,
    TranscoderStatus,
    TranscoderJob,
    VideoFrameAnalysis,
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
    'analyze-new-videos': {
        'task': 'src.tasks.cron.analyze_published_videos',
        'schedule': crontab(minute='*/5'),
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
            Video.published_at == None
        )

    for video in unpublished_videos:
        if is_video_published(video.id):
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
    pending_votes = session.query(Vote).filter(Vote.token_amount == None)

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
def analyze_published_videos():
    """ Refactoring todo:
        - break analysis and determination of outcome into 2 steps
        - break the snapshot processing into a small reusable function
        - parallelize the Rekognition calls
        - ensure 2 of the same videos arent being analyzed twice (if current task
          takes longer than the beat schedule). Perhaps can use TTL redis key as a lock.
    """
    session = db_session()
    videos = \
        (session.query(Video).filter(
            Video.analyzed_at == None,
            Video.published_at != None)
         .order_by(asc(Video.published_at))
         .limit(2))

    rkg = Rekognition()

    for video in videos:
        nsfw = []
        for snapshot in list_video_snapshots(video.id):
            nsfw_labels = rkg.nsfw(snapshot['Key'])
            labels = rkg.labels(snapshot['Key'])

            if labels or nsfw_labels:
                vfa = VideoFrameAnalysis(
                    frame_id=snapshot['Key'].split('/')[-1],
                    video_id=video.id,
                    labels=labels,
                    nsfw_labels=nsfw_labels,
                    created_at=dt.datetime.utcnow(),
                )
                session.add(vfa)
                nsfw.extend(nsfw_labels)

        # Needs to contain X (2) offending labels
        video.is_nsfw = bool(is_nsfw(nsfw) >= 2)
        video.analyzed_at = dt.datetime.utcnow()

        session.add(video)
        session.commit()

        # regen video manifest file to contain nsfw status
        generate_manifest_file.delay(video.id)


def list_video_snapshots(video_id, **kwargs):
    s3 = S3Transfer(bucket_name=S3_VIDEOS_BUCKET)
    result = s3.client.list_objects_v2(
        Bucket=S3_VIDEOS_BUCKET,
        MaxKeys=kwargs.get('max_keys', 100),
        Prefix=f'snapshots/{video_id}/random/')

    return result.get('Contents', [])


def is_nsfw(labels, filter_list=None, min_confidence=95, min_occurrence=2):
    """
    Return a number of high confidence, re-occurring labels
    that intersect the filtering list.
    """
    filter_list = filter_list or (
        'Explicit Nudity',
        'Graphic Nudity',
        'Graphic Female Nudity',
        'Graphic Male Nudity',
        'Sexual Activity',
    )

    labels = (x['Name'] for x in labels if x['Confidence'] > min_confidence)
    common_labels = {k: v for k, v in Counter(labels).items() if v >= min_occurrence}
    return len(set(common_labels) & set(filter_list))
