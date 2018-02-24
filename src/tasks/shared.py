import json
import time
from io import BytesIO
from typing import Union

import boto3

from . import (
    db_session,
    new_celery,
)
from ..config import (
    CDN_DISTRIBUTION_ID,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)
from ..config import S3_VIDEOS_REGION, S3_VIDEOS_BUCKET
from ..core.s3 import S3Transfer
from ..methods import generate_manifest
from ..models import (
    Video,
)

shared = new_celery(
    'thumbnails',
    include=['tasks.thumbnails'],
)
shared.conf.update(
    enable_utc=True,
    result_expires=3600,
)


@shared.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def invalidate_cdn_cache(s3_keys: list, reference_id: Union[str, int]):
    """ Invalidate CloudFront Cache.

    Args:
        s3_keys: List of S3 Keys in the distribution to invalidate
        reference_id: A random number or string to track the invalidation
    """
    if type(s3_keys) != list:
        s3_keys = [s3_keys]
    c = boto3.client(
        'cloudfront',
        aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
    )
    c.create_invalidation(
        DistributionId=CDN_DISTRIBUTION_ID,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(s3_keys),
                'Items': s3_keys,
            },
            'CallerReference': str(reference_id)
        })


@shared.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def generate_manifest_file(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()

    manifest_key = f"/v1/{video.id}/manifest.json"
    manifest = json.dumps(generate_manifest(video))

    s3 = S3Transfer(S3_VIDEOS_REGION, S3_VIDEOS_BUCKET)
    manifest_obj = BytesIO(bytes(manifest, 'utf-8'))
    s3.upload_fileobj(manifest_obj, manifest_key, overwrite=True)

    invalidate_cdn_cache.delay(
        s3_keys=[manifest_key],
        reference_id=str(time.time()),
    )
