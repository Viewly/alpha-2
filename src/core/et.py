import boto3
from funcy import lpluck

from ..config import (
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)
from ..config import elastic_transcoder as config


def get_job(transcoder_job_id: str):
    et = boto3.client(
        'elastictranscoder',
        region_name=config['region_name'],
        aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
    )
    return et.read_job(Id=transcoder_job_id)


def get_job_status(transcoder_job_id: str):
    return get_job(transcoder_job_id)['Job']['Status']


def extract_errors(transcoder_job: dict):
    from funcy import merge, where, lpluck
    job = transcoder_job['Job']
    outputs = merge(job['Outputs'], job['Playlists'])
    return lpluck('StatusDetail', where(outputs, Status='Error'))


def create_dash_job(
        input_key,
        output_path,
        video_resolution: tuple,
        has_audio: bool,
        segment_duration=6):
    segment_duration = str(segment_duration)

    # 720p input is minimum for DASH
    if video_resolution[0] < 1280 or video_resolution[1] < 720:
        return None, ''

    outputs = []
    if video_resolution[0] >= 1920 and video_resolution[1] >= 1080:
        outputs.append({
            'Key': '1080p',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['high']['1080p'],
            'SegmentDuration': segment_duration,
        })

    outputs.extend([
        {
            'Key': '480p',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['high']['480p'],
            'SegmentDuration': segment_duration,
        },
        {
            'Key': '720p',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['high']['720p'],
            'SegmentDuration': segment_duration,
        },
    ])

    if has_audio:
        outputs.append({
            'Key': 'audio',
            'PresetId': config['presets']['high']['audio'],
            'SegmentDuration': segment_duration,
        })

    et = boto3.client(
        'elastictranscoder',
        region_name=config['region_name'],
        aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
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
        Outputs=outputs,
        OutputKeyPrefix=output_path,
        Playlists=[
            {
                'Name': 'main',
                'Format': 'MPEG-DASH',
                'OutputKeys': lpluck('Key', outputs)
            },
        ],
        UserMetadata={},
    )

    return response, f"{output_path}main.mpd"


def create_fallback_job(
        input_key,
        output_path,
        video_resolution: tuple):
    if video_resolution[0] >= 1280 and video_resolution[1] >= 720:
        outputs = [{
            'Key': '720p.mp4',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['fallback']['720p'],
        }]
    elif video_resolution[0] >= 854 and video_resolution[1] >= 480:
        outputs = [{
            'Key': '480p.mp4',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['fallback']['480p'],
        }]
    else:
        outputs = [{
            'Key': '360p.mp4',
            'ThumbnailPattern': '',
            'Rotate': 'auto',
            'PresetId': config['presets']['fallback']['360p'],
        }]

    et = boto3.client(
        'elastictranscoder',
        region_name=config['region_name'],
        aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
        aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
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
        Outputs=outputs,
        OutputKeyPrefix=output_path,
        UserMetadata={},
    )

    return response, f"{output_path}{outputs[0]['Key']}"
