from . import (
    db_session,
    new_celery,
)
from .media import (
    img_resize_multi_to_s3,
    img_from_s3,
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

config = dict(
    input_region_name='us-west-2',
    input_bucket_name='viewly-uploads-test',
    output_region_name='us-west-2',
    output_bucket_name='viewly-videos-test',
)


@thumbnails.task(ignore_result=True)
def process_thumbnails(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).first()
    # download the original
    img = img_from_s3(
        video.file_mapper.s3_upload_thumbnail_key,
        region_name=config['input_region_name'],
        bucket_name=config['input_bucket_name'],
    )

    # resize into multiple sizes, compress
    sizes = img_resize_multi_to_s3(
        img,
        output_key_prefix=f'thumbnails/{video.id}/',
        region_name=config['output_region_name'],
        bucket_name=config['output_bucket_name'],
    )

    thumbnails = \
        {x['name']: f"{config['output_region_name']}:{config['output_bucket_name']}:"
                    f"/thumbnails/{video.id}/{x['file']}"
         for x in sizes}

    video.file_mapper.thumbnail_files = thumbnails
    session.add(video)
    session.commit()

# THUMBNAIL PIPELINE
# download the original
# resize into multiple sizes, compress
# publish to the CDN
