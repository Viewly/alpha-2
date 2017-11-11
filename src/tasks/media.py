import pathlib
import tempfile
from typing import List

from PIL import Image

from .s3 import S3Transfer


def img_from_s3(key: str):
    return Image.open(S3Transfer().download_bytes(key))


def img_resize_multi_s3(key: str, output_key_prefix: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = pathlib.Path(tmpdir)
        img_resize_multi(tmp_dir, img_from_s3(key))
        for file in tmp_dir.glob('*'):
            output_key = f'{output_key_prefix}/{file.name}'
            S3Transfer().upload_file(str(file), output_key)


def img_resize_multi(
        tmp_dir: pathlib.Path,
        img: Image,
        sizes: List[dict] = None,
        ext: str = 'png'):
    """
    Resize an original image into multiple sizes.
    Write the outputted files into a temporary directory.
    """
    sizes = sizes or [
        {'name': 'large', 'size': (1280, 720)},
        {'name': 'small', 'size': (640, 360)},
        {'name': 'tiny', 'size': (320, 180)},
        {'name': 'nano', 'size': (160, 90)},
    ]

    # todo: ShrinkToFit original into 16:9 ratio

    def resize(img, size, name):
        tmp_ = img.resize(size, Image.LANCZOS)
        tmp_.save(tmp_dir / f'{name}.{ext}')

    for size in sizes:
        if size['size'] > img.size:
            continue
        resize(img, size['size'], size['name'])
