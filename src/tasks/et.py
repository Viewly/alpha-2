import boto3

from ..config import elastic_transcoder as config


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
