from src.models import *
from src.tasks.thumbnails import *
from src.tasks.transcoder import *

# for tj in db.session.query(TranscoderJob).filter_by(preset_type='fallback'):
#     transcoder_post_processing.delay(tj.video_id, tj.id)
#
# for video in db.session.query(Video):
#     process_thumbnails.delay(video.id)

for video in db.session.query(Video):
    if video.published_at:
        process_thumbnails.delay(video.id)
        tj = db.session.query(TranscoderJob).filter_by(video_id=video.id, preset_type='fallback').one()
        transcoder_post_processing.delay(tj.id, video.id)
