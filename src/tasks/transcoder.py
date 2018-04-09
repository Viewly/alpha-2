from . import (
    db_session,
    new_celery,
)
from ..core.et import (
    create_dash_job,
    create_fallback_job,
    get_job,
)
from ..core.ffprobe import (
    get_video_resolution,
    has_audio_stream,
    get_video_framerate,
    get_duration,
)
from ..core.media import (
    run_ffprobe_s3,
    video_post_processing_s3,
)
from ..models import (
    Video,
    TranscoderStatus,
    TranscoderJob,
)
from .shared import generate_manifest_file

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
    transcoder_jobs = session.query(TranscoderJob).filter_by(video_id=video_id).all()
    if video and not transcoder_jobs:
        try:
            input_key = video.file_mapper.s3_upload_video_key
            output_path = f"v1/{video.id}"

            ffprobe_out = run_ffprobe_s3(input_key)
            if not ffprobe_out:
                # todo: mark transcoding as failed?
                return
            video.video_metadata = {
                'resolution': get_video_resolution(ffprobe_out),
                'framerate': get_video_framerate(ffprobe_out),
                'duration': get_duration(ffprobe_out),
            }

            fallback_job, fallback_key = create_fallback_job(
                input_key,
                output_path=f"{output_path}/fallback/",
                video_resolution=get_video_resolution(ffprobe_out),
            )
            dash_job, dash_key = create_dash_job(
                input_key,
                output_path=f"{output_path}/mpeg-dash/",
                video_resolution=get_video_resolution(ffprobe_out),
                has_audio=has_audio_stream(ffprobe_out),
            )

            # todo: this should be in refresh_transcoder_jobs(), because
            # if transcoding fails, this format will not be actually available
            video.file_mapper.video_formats = {
                'mpeg-dash': dash_key,
                'fallback': fallback_key,
            }
        except Exception as e:
            # todo: log the exception
            # todo: mark transcoding as failed
            print(e)
        else:
            if dash_job:
                session.add(TranscoderJob(
                    id=dash_job['Job']['Id'],
                    preset_type='mpeg-dash',
                    status=TranscoderStatus.processing,
                    video_id=video_id,
                ))
            if fallback_job:
                session.add(TranscoderJob(
                    id=fallback_job['Job']['Id'],
                    preset_type='fallback',
                    status=TranscoderStatus.processing,
                    video_id=video_id,
                ))

        session.add(video)
        session.commit()


@transcoder.task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
)
def transcoder_post_processing(video_id: str, transcoder_job_id: str):
    """
    Post Processing:
      - generate preview timelines
      - generate snapshots for ML Analysis
    """
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()
    tj = session.query(TranscoderJob).filter_by(
        id=transcoder_job_id, video_id=video_id).one()
    if tj.preset_type != 'fallback' or tj.status != TranscoderStatus.complete:
        return

    job = get_job(transcoder_job_id)
    input_key = "%s%s" % (
        job['Job']['OutputKeyPrefix'],
        job['Job']['Outputs'][0]['Key'])

    video.file_mapper.timeline_file = \
        video_post_processing_s3(
            key=input_key,
            s3_timeline_key_prefix=f"v1/{video.id}",
            s3_snapshots_key_prefix=f"snapshots/{video.id}",
            output_ext='jpg'
        )

    session.add(video)
    session.commit()

    generate_manifest_file.delay(video_id)
