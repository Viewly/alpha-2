import boto3

# output from deployment script, hard-coded for now
# TODO, load this dynamically from config file
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


def get_job(transcoder_job_id: str):
    et = boto3.client(
        'elastictranscoder',
        region_name=config['region_name']
    )
    return et.read_job(Id=transcoder_job_id)


def get_job_status(transcoder_job_id: str):
    return get_job(transcoder_job_id)['Job']['Status']


def extract_errors(transcoder_job: dict):
    from funcy import merge, where, lpluck
    job = transcoder_job['Job']
    outputs = merge(job['Outputs'], job['Playlists'])
    return lpluck('StatusDetail', where(outputs, Status='Error'))


def create_job(input_key, output_path, segment_duration=6):
    segment_duration = str(segment_duration)

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
                'PresetId': config['presets']['main']['480p'],
                'SegmentDuration': segment_duration,
            },
            {
                'Key': '720p',
                'ThumbnailPattern': '',
                'Rotate': 'auto',
                'PresetId': config['presets']['main']['720p'],
                'SegmentDuration': segment_duration,
            },
            {
                'Key': 'audio',
                'PresetId': config['presets']['main']['audio'],
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

    return response
