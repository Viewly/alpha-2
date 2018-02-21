from .models import (
    Video,
    TranscoderStatus,
)
from .config import CDN_URL


def get_manifest_cdn_url(video: Video):
    if video.transcoder_status == TranscoderStatus.complete:
        return \
            f"{CDN_URL}/{video.file_mapper.video_manifest_version}" \
            f"/{video.id}/dash.mpd"


def get_thumbnail_cdn_url(video: Video, size_name='small'):
    thumbnail_files = video.file_mapper.thumbnail_files
    if thumbnail_files and size_name in thumbnail_files:
        key = thumbnail_files.get(size_name).split(':')[-1]
        return f"{CDN_URL}/{key.lstrip('/')}"


def get_video_cdn_assets(video: Video):
    # TODO: degrade gracefully if large thumbnail size not available
    return {
        'video': get_manifest_cdn_url(video),
        'poster': get_thumbnail_cdn_url(video, 'small'),
    }


def guess_thumbnail_cdn_url(video_id: str, size_name='small'):
    # TODO: rather than guessing, this should be cached
    return f"{CDN_URL}/thumbnails/{video_id}/{size_name}.png"
