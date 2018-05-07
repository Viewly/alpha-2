import json
import time
from io import BytesIO
from typing import Union
from funcy import lkeep

import boto3

from . import (
    db_session,
    new_celery,
)
from ..config import (
    CDN_DISTRIBUTION_ID,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
    S3_VIDEOS_REGION,
    S3_VIDEOS_BUCKET,
    S3_UPLOADS_REGION,
)
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


@shared.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def delete_video_files(video_id: str, file_mapper_obj: dict):
    # delete upload files
    s3 = boto3.client(
        's3',
        region_name=S3_UPLOADS_REGION,
        aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
    )
    keys_to_delete = lkeep([
        file_mapper_obj['s3_upload_video_key'],
        file_mapper_obj['s3_upload_thumbnail_key'],
    ])
    s3.delete_objects(
        Bucket=file_mapper_obj['s3_upload_bucket'],
        Delete={
            'Objects': [{'Key': x} for x in keys_to_delete],
        },
    )

    # delete video files
    s3t = S3Transfer(
        region_name=S3_VIDEOS_REGION,
        bucket_name=S3_VIDEOS_BUCKET,
    )
    keys_to_delete = [
        *s3t.ls(f'snapshots/{video_id}'),
        *s3t.ls(f'thumbnails/{video_id}'),
        *s3t.ls(f'v1/{video_id}'),
    ]
    if keys_to_delete:
        s3t.client.delete_objects(
            Bucket=S3_VIDEOS_BUCKET,
            Delete={
                'Objects': [{'Key': x['Key']} for x in keys_to_delete],
            },
        )
