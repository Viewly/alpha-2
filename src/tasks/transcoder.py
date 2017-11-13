import boto3

from . import (
    db_session,
    new_celery,
)
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

# output from deployment script, hard-coded for now
config = {
    "pipeline_id": "1510584356879-m06i3i",
    "pipeline_name": "test-pipeline-3",
    "presets": {
        "high": {
            "1080p": "1510584361870-if0nc5",
            "480p": "1510584361409-1dcqrs",
            "720p": "1510584361639-3b0rh6",
            "audio": "1510584360931-igwhnz"
        },
        "main": {
            "480p": "1510584359774-j6gnfd",
            "720p": "1510584360503-la02m0",
            "audio": "1510584360931-igwhnz"
        }
    },
    "region_name": "us-west-2",
    "s3_input_bucket": "viewly-uploads-test",
    "s3_output_bucket": "viewly-videos-test",
    "sns": {
        "completed": "arn:aws:sns:us-west-2:643658388652:viewly-transcoder-completed",
        "error": "arn:aws:sns:us-west-2:643658388652:viewly-transcoder-error",
        "processing": "arn:aws:sns:us-west-2:643658388652:viewly-transcoder-processing",
        "warning": "arn:aws:sns:us-west-2:643658388652:viewly-transcoder-warning"
    }
}


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
    is_pending = not video.transcoder_status or video.transcoder_status == TranscoderStatus.pending
    if video and is_pending:
        try:
            input_key = video.file_mapper.s3_upload_video_key
            output_path = f"{video.user_id}/{video.id}"
            presets = config['presets']
            segment_duration = '6'
            et = boto3.client(
                'elastictranscoder',
                region_name=config['region_name']
            )
            response = et.create_job(
                PipelineId=config['pipeline_id'],
                Input={
                    'Key': input_key,
                    'FrameRate': 'auto',
                    'Resolution': 'auto',
                    'AspectRatio': 'auto',
                    'Interlaced': 'auto',
                    'Container': 'auto',
                },
                Outputs=[
                    {
                        'Key': '480p',
                        'ThumbnailPattern': '',
                        'Rotate': 'auto',
                        'PresetId': presets['main']['480p'],
                        'SegmentDuration': segment_duration,
                    },
                    {
                        'Key': '720p',
                        'ThumbnailPattern': '',
                        'Rotate': 'auto',
                        'PresetId': presets['main']['720p'],
                        'SegmentDuration': segment_duration,
                    },
                    {
                        'Key': 'audio',
                        'PresetId': presets['main']['audio'],
                        'SegmentDuration': segment_duration,
                    },
                ],
                OutputKeyPrefix=output_path,
                Playlists=[
                    {
                        'Name': 'dash-main',
                        'Format': 'MPEG-DASH',
                        'OutputKeys': [
                            '480p',
                            '720p',
                            'audio',
                        ],
                    },
                ],
                UserMetadata={},
            )
        except Exception as e:
            # todo: log the exception
            video.transcoder_status = TranscoderStatus.failed
            print(e)
        else:
            video.transcoder_status = TranscoderStatus.processing
            video.transcoder_job_id = response['Job']['Id']
            video.transcoder_pipeline = config['pipeline_id']

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
