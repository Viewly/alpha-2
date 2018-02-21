import json

import delegator
from funcy import lpluck, lwhere, first


def run_ffprobe(video_path: str):
    command = f'ffprobe -show_format -show_streams' \
              f' -loglevel quiet -print_format json {video_path}'
    output = delegator.run(command).out
    return json.loads(output)


def has_audio_stream(ffprobe_out: dict) -> bool:
    streams = ffprobe_out.get('streams', {})
    return 'audio' in lpluck('codec_type', streams)


def get_video_stream(ffprobe_out: dict) -> dict:
    video_streams = lwhere(ffprobe_out.get('streams', {}), codec_type='video')
    return first(video_streams)


def get_video_resolution(ffprobe_out: dict) -> tuple:
    video = get_video_stream(ffprobe_out)
    return video['coded_width'], video['coded_height']


def get_video_framerate(ffprobe_out: dict) -> int:
    video = get_video_stream(ffprobe_out)
    return int(first(video['r_frame_rate'].split('/')))


def get_duration(ffprobe_out: dict) -> float:
    return float(ffprobe_out.get('format', {}).get('duration'))


def get_bitrate(ffprobe_out: dict) -> int:
    return int(ffprobe_out.get('format', {}).get('bit_rate'))


def get_size(ffprobe_out: dict) -> int:
    return int(ffprobe_out.get('format', {}).get('size'))
