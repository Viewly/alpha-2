from . import (
    db_session,
    new_celery,
)
from .et import create_job
from ..models import Video, TranscoderStatus

transcoder = new_celery(
    'transcoder',
    include=['src.tasks.transcoder'],
)
transcoder.conf.update(
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)


@transcoder.task(ignore_result=True)
def analyze_video(video_id: str):
    pass


@transcoder.task(ignore_result=True)
def generate_snapshots(video_id: str):
    pass


@transcoder.task(ignore_result=True)
def generate_timeline(video_id: str):
    pass


@transcoder.task(ignore_result=True)
def start_transcoder_job(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()
    is_pending = not video.transcoder_status \
                 or video.transcoder_status == TranscoderStatus.pending
    if video and is_pending:
        try:
            input_key = video.file_mapper.s3_upload_video_key
            output_path = f"v1/{video.id}"
            response = create_job(input_key, output_path)
        except Exception as e:
            # todo: log the exception
            video.transcoder_status = TranscoderStatus.failed
            print(e)
        else:
            video.transcoder_status = TranscoderStatus.processing
            video.transcoder_job_id = response['Job']['Id']

        session.add(video)
        session.commit()

# VIDEO PIPELINE
# download the video
# analyze the video (format, encoding, size, resolution, etc)
# if invalid, delete it, and invalidate upload
# if valid, kick off the transcoder job
# once the transcoding is done:
# generate the timeline from 720p version
# generate the snapshots for ML analysis
# generate the transcriptions (for ml, subtitles, seo)
# generate the metadata file for embedded player
