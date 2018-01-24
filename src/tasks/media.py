import pathlib
import tempfile
from fractions import Fraction
from typing import List, Dict

from PIL import Image, ImageOps

from .s3 import S3Transfer


def img_from_s3(key: str, **kwargs) -> Image:
    return Image.open(
        S3Transfer(**kwargs).download_bytes(key)
    )


def img_resize_multi_to_s3(image: Image, output_key_prefix: str, **kwargs):
    """ Takes an input image from `key` and stores resized
    images in `output_key_prefix`.

    Args:
        image: Pillow in-memory image
        output_key_prefix: can be something like "v1/{video_id}/thumbnails"
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = pathlib.Path(tmpdir)
        available_sizes = img_resize_multi(tmp_dir, image)

        s3_transfer = S3Transfer(**kwargs)
        for file in tmp_dir.glob('*'):
            output_key = f'{output_key_prefix}/{file.name}'
            s3_transfer.upload_file(str(file), output_key)

    return available_sizes


def img_resize_multi(
        tmp_dir: pathlib.Path,
        img: Image,
        sizes: List[Dict] = None,
        output_ext: str = 'png') -> list:
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

    # ShrinkToFit original img into 16:9 ratio
    if Fraction(*img.size) != Fraction(16, 9):
        resizer = lambda size: ImageOps.fit(img, size=size, method=Image.LANCZOS)
    else:
        resizer = lambda size: img.resize(size, Image.LANCZOS)

    available_sizes = []
    for size in filter(lambda x: img.size >= x['size'], sizes):
        file_name = '%s.%s' % (size['name'], output_ext)
        available_sizes.append({**size, 'file': file_name})
        tmp_ = resizer(size['size'])
        tmp_.save(tmp_dir / file_name)

    return available_sizes
