from .models import (
    Video,
    TranscoderStatus,
)


def get_manifest_cdn_url(video: Video):
    if video.transcoder_status == TranscoderStatus.complete:
        # TODO: dynamic distribution ID
        return \
            f"http://d27z8otvfx49ba.cloudfront.net" \
            f"/{video.file_mapper.video_manifest_version}/{video.id}/dash-main.mpd"


def get_thumbnail_cdn_url(video: Video, size_name='small'):
    thumbnail_files = video.file_mapper.thumbnail_files
    if thumbnail_files and size_name in thumbnail_files:
        key = thumbnail_files.get(size_name).split(':')[-1]
        # TODO: dynamic distribution ID
        return f"http://d27z8otvfx49ba.cloudfront.net/{key.lstrip('/')}"


def get_video_cdn_assets(video: Video):
    # TODO: degrade gracefully if large thumbnail size not available
    return {
        'video': get_manifest_cdn_url(video),
        'poster': get_thumbnail_cdn_url(video, 'small'),
    }
