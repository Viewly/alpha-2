from . import new_celery

transcoder = new_celery(
    'transcoder',
    include=['tasks.transcoder'],
)
transcoder.conf.update(
    enable_utc=True,
    result_expires=3600,
)


@transcoder.task(ignore_result=True)
def analyze_video(video_id: str):
    pass


@transcoder.task(ignore_result=True)
def generate_snapshots(video_id: str):
    pass


@transcoder.task(ignore_result=True)
def generate_timeline(video_id: str):
    pass

# VIDEO PIPELINE
# download the video
# analyze the video (format, encoding, size, resolution, etc)
# if invalid, delete it, and invalidate upload
# if valid, kick off the transcoder job
# once the transcoding is done:
# generate the timeline from 720p version
# generate the snapshots for ML analysis
# generate the transcriptions (for ml, subtitles, seo)
# generate the metadata file for embedded player
