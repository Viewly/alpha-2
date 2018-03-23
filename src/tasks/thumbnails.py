import time

from . import (
    db_session,
    new_celery,
)
from .shared import (
    generate_manifest_file,
    invalidate_cdn_cache,
)
from ..config import (
    S3_UPLOADS_BUCKET,
    S3_UPLOADS_REGION,
    S3_VIDEOS_BUCKET,
    S3_VIDEOS_REGION,
)
from ..core.media import (
    img_resize_multi_to_s3,
    img_from_s3,
    MinResNotAvailableError,
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
    video = session.query(Video).filter_by(id=video_id).one()
    # download the original
    img = img_from_s3(
        video.file_mapper.s3_upload_thumbnail_key,
        region_name=S3_UPLOADS_REGION,
        bucket_name=S3_UPLOADS_BUCKET,
    )

    # resize into multiple sizes, compress
    try:
        sizes = img_resize_multi_to_s3(
            image=img,
            min_size_name='small',
            output_key_prefix=f'thumbnails/{video.id}/',
            region_name=S3_VIDEOS_REGION,
            bucket_name=S3_VIDEOS_BUCKET,
        )
    except MinResNotAvailableError:
        # todo, delete actual s3 file as well
        video.file_mapper.s3_upload_thumbnail_key = None
    else:
        # if thumbnails existed previously, invalidate CDN cache
        thumbnail_files = video.file_mapper.thumbnail_files
        if thumbnail_files:
            invalidate_cdn_cache.delay(
                s3_keys=[f"/{x}" for x in thumbnail_files.values()],
                reference_id=str(time.time()),
            )
        video.file_mapper.thumbnail_files = \
            {x['name']: f"thumbnails/{video.id}/{x['file']}" for x in sizes}

        generate_manifest_file.delay(video.id)

    session.add(video)
    session.commit()

# THUMBNAIL PIPELINE
# download the original
# resize into multiple sizes, compress
# publish to the CDN
