from .config import CDN_URL


def generate_manifest(video):
    return {
        'formats': video.file_mapper.video_formats,
        'cover': get_thumbnail(video, 'large'),
        'timeline': video.file_mapper.timeline_file,
        'info': {
            'duration': video.video_metadata.get('duration', 0),
        }
    }


def get_thumbnail(video, preferred_size='large', fallback_size='tiny'):
    """ Get the largest possible size if preferred size is not available"""
    thumbnail_files = video.file_mapper.thumbnail_files
    if thumbnail_files:
        return thumbnail_files.get(
            preferred_size,
            thumbnail_files.get(fallback_size, '')
        )

    return ''


def get_thumbnail_cdn_url(*args, **kwargs):
    thumbnail = get_thumbnail(*args, **kwargs)
    if thumbnail:
        return f"{CDN_URL}/{thumbnail}"


def guess_thumbnail_cdn_url(video_id: str, size_name='tiny'):
    return f"{CDN_URL}/thumbnails/{video_id}/{size_name}.jpg"


def guess_avatar_cdn_url(channel_id: str, size_name='tiny'):
    return f"{CDN_URL}/avatars/{channel_id}/{size_name}.png"


def guess_timeline_cdn_url(video_id: str, timeline_file: str):
    return f"{CDN_URL}/v1/{video_id}/{timeline_file}"
