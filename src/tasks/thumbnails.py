from . import (
    db_session,
    new_celery,
)
from .media import (
    img_resize_multi_to_s3,
    img_from_s3,
)
from ..config import (
    S3_UPLOADS_BUCKET,
    S3_UPLOADS_REGION,
    S3_VIDEOS_BUCKET,
    S3_VIDEOS_REGION,
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

    thumbs = \
        {x['name']: f"{S3_VIDEOS_REGION}:{S3_VIDEOS_BUCKET}:"
                    f"/thumbnails/{video.id}/{x['file']}"
         for x in sizes}

    video.file_mapper.thumbnail_files = thumbs
    session.add(video)
    session.commit()

# THUMBNAIL PIPELINE
# download the original
# resize into multiple sizes, compress
# publish to the CDN
