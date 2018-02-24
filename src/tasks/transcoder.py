import json
from io import BytesIO

from . import (
    db_session,
    new_celery,
)
from ..config import S3_VIDEOS_REGION, S3_VIDEOS_BUCKET
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
from ..core.s3 import S3Transfer
from ..models import (
    Video,
    TranscoderStatus,
    TranscoderJob,
)

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
    retry_kwargs={'max_retries': 3},
)
def generate_manifest_file(video_id: str):
    session = db_session()
    video = session.query(Video).filter_by(id=video_id).one()

    manifest_key = f"v1/{video.id}/manifest.json"
    manifest = json.dumps(generate_manifest(video))

    s3 = S3Transfer(S3_VIDEOS_REGION, S3_VIDEOS_BUCKET)
    manifest_obj = BytesIO(bytes(manifest, 'utf-8'))
    s3.upload_fileobj(manifest_obj, manifest_key, overwrite=True)


def generate_manifest(video: Video):
    return {
        'formats': video.file_mapper.video_formats,
        'cover': video.file_mapper.thumbnail_files['small'].split('/')[1],
        'timeline': '',
        'info': {
            'duration': video.video_metadata.get('duration', 0),
        }
    }


# VIDEO PIPELINE
# once the transcoding is done:
# generate the timeline from 720p version
# generate the snapshots for ML analysis
# generate the transcriptions (for ml, subtitles, seo)
# generate the metadata file for embedded player
