import time
from typing import Union

import boto3

from . import (
    db_session,
    new_celery,
)
from ..core.media import (
    img_resize_multi_to_s3,
    img_from_s3,
)
from ..config import (
    S3_UPLOADS_BUCKET,
    S3_UPLOADS_REGION,
    S3_VIDEOS_BUCKET,
    S3_VIDEOS_REGION,
    CDN_DISTRIBUTION_ID,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)
from ..models import Video

thumbnails = new_celery(
    'thumbnails',
    include=['tasks.thumbnails'],
)
thumbnails.conf.update(
    enable_utc=True,
    result_expires=3600,
)


@thumbnails.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def process_thumbnails(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).first()
    # download the original
    img = img_from_s3(
        video.file_mapper.s3_upload_thumbnail_key,
        region_name=S3_UPLOADS_REGION,
        bucket_name=S3_UPLOADS_BUCKET,
    )

    # resize into multiple sizes, compress
    sizes = img_resize_multi_to_s3(
        img,
        output_key_prefix=f'thumbnails/{video.id}/',
        region_name=S3_VIDEOS_REGION,
        bucket_name=S3_VIDEOS_BUCKET,
    )

    # if thumbnails existed previously, invalidate CDN cache
    thumbnail_files = video.file_mapper.thumbnail_files
    if thumbnail_files:
        invalidate_cdn_cache.delay(
            s3_keys=[x.split(':')[-1] for x in thumbnail_files.values()],
            reference_id=str(time.time()),
        )

    thumbs = \
        {x['name']: f"{S3_VIDEOS_REGION}:{S3_VIDEOS_BUCKET}:"
                    f"/thumbnails/{video.id}/{x['file']}"
         for x in sizes}

    video.file_mapper.thumbnail_files = thumbs
    session.add(video)
    session.commit()


@thumbnails.task(
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

# THUMBNAIL PIPELINE
# download the original
# resize into multiple sizes, compress
# publish to the CDN
