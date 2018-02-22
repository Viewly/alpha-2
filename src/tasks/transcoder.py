from . import (
    db_session,
    new_celery,
)
from ..core.et import (
    create_dash_job,
    create_fallback_job,
)
from ..core.ffprobe import (
    get_video_resolution,
    has_audio_stream,
    get_video_framerate,
    get_duration,
)
from ..core.media import run_ffprobe_s3
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


@transcoder.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
)
def start_transcoder_job(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()
    is_pending = not video.transcoder_status \
                 or video.transcoder_status == TranscoderStatus.pending
    if video and is_pending:
        try:
            input_key = video.file_mapper.s3_upload_video_key
            output_path = f"v1/{video.id}/"

            ffprobe_out = run_ffprobe_s3(input_key)
            if not ffprobe_out:
                # todo: mark transcoding as failed?
                return
            video.video_metadata = {
                'resolution': get_video_resolution(ffprobe_out),
                'framerate': get_video_framerate(ffprobe_out),
                'duration': get_duration(ffprobe_out),
            }

            fallback = create_fallback_job(
                input_key,
                output_path,
                video_resolution=get_video_resolution(ffprobe_out),
            )
            dash = create_dash_job(
                input_key,
                output_path,
                video_resolution=get_video_resolution(ffprobe_out),
                has_audio=has_audio_stream(ffprobe_out),
            )
        except Exception as e:
            # todo: log the exception
            video.transcoder_status = TranscoderStatus.failed
            print(e)
        else:
            video.transcoder_status = TranscoderStatus.processing
            video.transcoder_job_id = fallback['Job']['Id']

        session.add(video)
        session.commit()

# VIDEO PIPELINE
# once the transcoding is done:
# generate the timeline from 720p version
# generate the snapshots for ML analysis
# generate the transcriptions (for ml, subtitles, seo)
# generate the metadata file for embedded player
