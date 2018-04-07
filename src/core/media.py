import math
import os
import pathlib
import random
import tempfile
from fractions import Fraction
from typing import List, Dict, Union

from PIL import Image, ImageOps
from funcy import lpluck, chunks, first, last

from .ffprobe import (
    run_ffprobe
)
from .s3 import S3Transfer
from .utils import ensure_directory, cleanup
from ..config import (
    S3_VIDEOS_BUCKET,
    S3_VIDEOS_REGION,
)


def run_ffprobe_s3(key: str, **kwargs):
    s3_transfer = S3Transfer(**kwargs)
    with tempfile.TemporaryDirectory() as tmp_dir:
        video_file = str(pathlib.Path(tmp_dir) / 'video.tmp')
        s3_transfer.download_file(key, video_file)
        return run_ffprobe(video_file)


def img_from_s3(key: str, **kwargs) -> Image:
    return Image.open(
        S3Transfer(**kwargs).download_bytes(key)
    )


def img_resize_multi_to_s3(image: Image, s3_output_key_prefix: str, **kwargs):
    """ Takes an input image from `key` and stores resized
    images in `output_key_prefix`.

    Args:
        image: Pillow in-memory image
        s3_output_key_prefix: can be something like "v1/{video_id}/thumbnails"
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = pathlib.Path(tmpdir)
        available_sizes = img_resize_multi(tmp_dir, image, **kwargs)

        s3_transfer = S3Transfer(**kwargs)
        for file in tmp_dir.glob('*'):
            output_key = f'{s3_output_key_prefix.rstrip("/")}/{file.name}'
            s3_transfer.upload_file(str(file), output_key)

    return available_sizes


def img_resize_multi(
        tmp_dir: pathlib.Path,
        img: Image,
        sizes: List[Dict] = None,
        min_size_name: str = None,
        aspect_ratio: tuple = (16, 9), **kwargs) -> list:
    """
    Resize an original image into multiple sizes.
    Write the outputted files into a temporary directory.

    Returns a list of available resolutions.
    """
    sizes = sizes or [
        {'name': 'large', 'size': (1280, 720)},
        {'name': 'small', 'size': (640, 360)},
        {'name': 'tiny', 'size': (320, 180)},
        {'name': 'nano', 'size': (160, 90)},
    ]

    available_sizes = []
    for size in filter(lambda x: larger_or_equal_size(img.size, x['size']), sizes):
        file_name = '%s.%s' % (size['name'], kwargs.get("output_ext", "png"))
        available_sizes.append({**size, 'file': file_name})
        tmp_ = img_resize(img, size['size'], aspect_ratio=aspect_ratio)
        tmp_.save(tmp_dir / file_name)

    if min_size_name \
            and min_size_name not in lpluck('name', available_sizes):
        raise MinResNotAvailableError

    return available_sizes


def img_resize(img: Image, size: tuple, aspect_ratio: tuple = (16, 9)):
    if Fraction(*img.size) != Fraction(*aspect_ratio):
        return ImageOps.fit(img, size=size, method=Image.LANCZOS)
    return img.resize(size, Image.LANCZOS)


def larger_or_equal_size(first: tuple, second: tuple):
    return first[0] >= second[0] and first[1] >= second[1]


class MinResNotAvailableError(BaseException):
    pass


def video_post_processing_s3(
        key: str,
        s3_timeline_key_prefix: str,
        s3_snapshots_key_prefix: str, **kwargs) -> Union[str, None]:
    """
    Given a video file, do the following:
     - download the video from S3
     - generate preview images and stitch together a preview tile
     - generate random snapshots for ml purposes
     - upload the preview tile and random snapshots back to S3

    Returns:
        A filename of the tile sheet containing meta-embedded properties.
    """
    s3_transfer = S3Transfer(
        region_name=S3_VIDEOS_REGION, bucket_name=S3_VIDEOS_BUCKET, **kwargs)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = pathlib.Path(tmpdir)

        # download the video
        video_file = str(tmp_dir / 'video.tmp')
        s3_transfer.download_file(key, video_file)

        # generate timed snapshots for preview tiles
        ensure_directory(str(tmp_dir / 'timeline'))
        window_seconds = generate_preview_images(tmp_dir, video_file)
        if not window_seconds:
            return
        tile_sheet_name = stitch_tile_sheet(tmp_dir, window_seconds)
        tile_sheet_path = str(tmp_dir / tile_sheet_name)
        s3_transfer.upload_file(
            tile_sheet_path,
            f'{s3_timeline_key_prefix.rstrip("/")}/{tile_sheet_name}')
        cleanup([tile_sheet_path, str(tmp_dir / 'timeline')])

        # generate random snapshots for machine learning
        ensure_directory(str(tmp_dir / 'random'))
        generate_random_images(tmp_dir, video_file)

        # upload snapshots to s3
        # todo: upload these as "reduced redundancy" to save $$
        for file in tmp_dir.rglob('*.%s' % kwargs.get("output_ext", "png")):
            output_key = f'{s3_snapshots_key_prefix.rstrip("/")}/' \
                         f'{file.relative_to(tmp_dir)}'
            s3_transfer.upload_file(str(file), output_key)

    return tile_sheet_name


def generate_random_images(
        tmp_directory,
        video_file,
        size=None,
        aspect_ratio=(16, 9), **kwargs):
    """ Generate uniformly distributed random snapshots from a video."""
    from moviepy import editor
    clip = editor.VideoFileClip(video_file)

    if int(clip.duration) < 1:
        return 0

    # hard-coded steps of snapshot smoothness
    if clip.duration < 30:
        num_of_chunks = 3
    elif clip.duration < 60:
        num_of_chunks = 5
    elif clip.duration < 60 * 5:
        num_of_chunks = 20
    elif clip.duration < 60 * 10:
        num_of_chunks = 30
    else:
        num_of_chunks = 50

    chunk_size = int(clip.duration // num_of_chunks)
    for i, video_chunk in enumerate(chunks(chunk_size, range(0, int(clip.duration)))):
        random_frame_time = random.uniform(first(video_chunk), last(video_chunk))
        img = Image.fromarray(clip.get_frame(random_frame_time))
        if size:
            img = img_resize(img, size=size, aspect_ratio=aspect_ratio)
        file_name = f'{i}.{kwargs.get("output_ext", "png")}'
        img.save(str(tmp_directory / 'random' / file_name))

    return num_of_chunks


def generate_preview_images(
        tmp_directory,
        video_file,
        size=(192, 108),
        aspect_ratio=(16, 9), **kwargs):
    """ Generate small resolution, periodic frame snapshots from a video. """
    from moviepy import editor
    clip = editor.VideoFileClip(video_file)

    if int(clip.duration) < 1:
        return 0

    # hard-coded steps of snapshot smoothness
    if clip.duration < 15:
        window_seconds = 1
    elif clip.duration < 60:
        window_seconds = 3
    elif clip.duration < 60 * 5:
        window_seconds = 5
    elif clip.duration < 60 * 10:
        window_seconds = 10
    elif clip.duration < 60 * 30:
        window_seconds = 15
    else:
        window_seconds = 30

    ensure_directory(os.path.join(tmp_directory, 'timeline'))
    for i in range(0, int(clip.duration), window_seconds):  # capture every N'th second
        img = Image.fromarray(clip.get_frame(i))
        if size:
            img = img_resize(img, size=size, aspect_ratio=aspect_ratio)
        file_name = f'{i}.{kwargs.get("output_ext", "png")}'
        img.save(str(tmp_directory / 'timeline' / file_name))

    return window_seconds


def stitch_tile_sheet(tmp_directory, window_seconds=5, **kwargs) -> Image:
    """
    Take the output of generate_preview_images, and stitch all images into
    a grid based tile image.
    """
    ext = kwargs.get("output_ext", "png")
    # sort frames by filenames
    timeline_dir = os.path.join(tmp_directory, 'timeline')
    timeline_filenames = sorted([int(x.split('.')[0]) for x in os.listdir(timeline_dir)])
    files = [os.path.join(timeline_dir, f'{x}.{ext}') for x in timeline_filenames]

    if not files:
        return

    frames = list(map(image_from_file, files))

    max_frames_row = 10
    tile_width = frames[0].size[0]
    tile_height = frames[0].size[1]

    if len(frames) > max_frames_row:
        spritesheet_width = tile_width * max_frames_row
        required_rows = math.ceil(len(frames) / max_frames_row)
        spritesheet_height = tile_height * required_rows
    else:
        spritesheet_width = tile_width * len(frames)
        spritesheet_height = tile_height

    spritesheet = Image.new("RGBA", (int(spritesheet_width), int(spritesheet_height)))

    for current_frame in frames:
        top = tile_height * math.floor((frames.index(current_frame)) / max_frames_row)
        left = tile_width * (frames.index(current_frame) % max_frames_row)
        bottom = top + tile_height
        right = left + tile_width

        box = (left, top, right, bottom)
        box = [int(i) for i in box]
        cut_frame = current_frame.crop((0, 0, tile_width, tile_height))

        spritesheet.paste(cut_frame, box)

    file_name = "tilesheet_%d_%d_%d_%d.%s" % (
        len(frames), window_seconds, tile_width, tile_height, ext)
    spritesheet.save(os.path.join(tmp_directory, file_name))

    return file_name


def image_from_file(file_path: str) -> Image:
    """ Load PIL Image from file"""
    with Image.open(file_path) as img:
        return img.getdata()
