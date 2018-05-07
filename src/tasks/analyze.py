import datetime as dt
from collections import Counter

from . import (
    new_celery,
    db_session,
)
from .shared import generate_manifest_file
from ..config import (
    S3_VIDEOS_BUCKET,
)
from ..core.rkg import Rekognition
from ..core.s3 import S3Transfer
from ..models import (
    Video,
    VideoFrameAnalysis,
)

analyze = new_celery(
    'analyze',
    include=['tasks.analyze'],
)
analyze.conf.update(
    enable_utc=True,
    result_expires=3600,
)


@analyze.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def extract_labels_from_video(video_id):
    """
    Warning:
    This method should be called AFTER video post-processing is complete.

    Todo:
      - split label extraction from NSFW classification into 2 steps
    """
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()
    # assert video.published_at is not None,\
    #     'Cannot extract labels on un unpublished video'

    rkg = Rekognition()

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

    # Needs to contain at least 3 offending labels
    video.is_nsfw = bool(is_nsfw(nsfw) >= 3)
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
