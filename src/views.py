import datetime as dt
import json
from typing import Union

import maya
from flask import (
    render_template,
    request,
    jsonify,
    abort,
)
from flask_security import (
    current_user,
    login_required,
)
from sqlalchemy import desc, func

from . import app, db
from .methods import (
    guess_thumbnail_cdn_url,
    guess_avatar_cdn_url,
)
from .models import Video, Channel, TranscoderJob


# router
# ------
@app.route('/')
def index():
    return new()


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/v/<string:video_id>', methods=['GET'])
def view_video(video_id):
    video = Video.query.filter_by(id=video_id).first_or_404()
    if not video.published_at and not is_owner(video.user_id):
        return abort(404)
    return render_template('view.html', video=video)


@app.route('/embed/<string:video_id>', methods=['GET'])
def embed(video_id):
    return render_template(
        'embed.html',
        video_id=video_id,
        autoPlay=request.args.get('autoPlay', True),
    )


@app.route('/c/<string:channel_id>', methods=['GET'])
def view_channel(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    videos = \
        Video.query.filter_by(channel_id=channel_id).order_by(desc(Video.published_at))

    # do not show unpublished videos to public
    if not is_owner(channel.user_id):
        videos = videos.filter(Video.published_at != None)

    return render_template(
        'channel.html',
        channel=channel,
        videos=videos.limit(10).all(),
        s3_bucket_name=app.config['S3_UPLOADS_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADS_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
    )


@app.route('/search', methods=['GET'])
def search(page_num=0, items_per_page=20):
    limit = items_per_page
    page_num = page_num or int(request.args.get('page', 0))

    search_query = request.args.get('q')
    q = """
    SELECT v.id, v.title,
           v.video_metadata,
           c.display_name AS channel_name, c.id AS channel_id
    FROM video v LEFT JOIN channel c
    ON v.channel_id = c.id
    WHERE to_tsvector(v.title || ' ' || v.description) @@ plainto_tsquery(:search)
     AND v.published_at IS NOT NULL
    ORDER BY v.published_at DESC
    LIMIT :limit OFFSET :offset;
    """

    rs = db.session.execute(q, {
        "search": search_query,
        "limit": limit,
        "offset": limit * page_num,
    })
    results = [dict(zip(rs.keys(), item)) for item in rs.fetchall()]

    return render_template(
        'search.html',
        results=results,
        query=search_query,
        page_num=page_num,
        items_per_page=items_per_page,
    )


@app.route('/new', methods=['GET'])
def new(page_num=0, items_per_page=18):
    limit = items_per_page
    page_num = page_num or int(request.args.get('page', 0))

    videos = (db.session.query(Video)
              .filter(Video.published_at != None, Video.channel_id != None)
              .order_by(desc(Video.published_at))
              .limit(limit).offset(limit * page_num).all())

    return render_template(
        'new.html',
        videos=videos,
        page_num=page_num,
        items_per_page=items_per_page,
    )


@app.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    """
    select channel.*, count(video.id) as video_count
     from channel
     left join video on video.channel_id = channel.id
     group by channel.id
     having channel.user_id = :user_id;
    """
    channels = db.session.query(Channel, func.count(Video.id).label('video_count')) \
        .outerjoin(Video) \
        .group_by(Channel) \
        .having(Channel.user_id == current_user.id) \
        .order_by(desc('video_count'))
    return render_template(
        'edit_profile.html',
        channels=channels,
    )


@app.route('/auth_token', methods=['GET'])
@login_required
def auth_token():
    return jsonify({'auth_token': current_user.get_auth_token()})


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


# template helpers
# ----------------
@app.context_processor
def utility_processor():
    def block_num():
        return 0

    def get_transcoding_status(video_id: str):
        job = TranscoderJob.query.filter_by(
            video_id=video_id,
            preset_type='fallback').first()
        if job:
            return job.status.name
        return 'pending'

    return dict(
        block_num=block_num,
        get_transcoding_status=get_transcoding_status,
        guess_thumbnail_cdn_url=guess_thumbnail_cdn_url,
        guess_avatar_cdn_url=guess_avatar_cdn_url,
        virtual_host=lambda: app.config['VIRTUAL_HOST'].rstrip('/'),
        cdn_url=lambda: app.config['CDN_URL'],
        eth_chain=lambda: app.config['ETH_CHAIN'],
        view_token_abi=lambda: json.dumps(app.config['VIEW_TOKEN_ABI']),
        video_publisher_abi=lambda: json.dumps(app.config['VIDEO_PUBLISHER_ABI']),
        view_token_address=lambda: app.config['VIEW_TOKEN_ADDRESS'],
        video_publisher_address=lambda: app.config['VIDEO_PUBLISHER_ADDRESS'],
    )


@app.template_filter('humanDate')
def human_date(dto: dt.datetime):
    if not dto:
        return ''
    if type(dto) == str:
        dto = maya.parse(dto).datetime()
    return dto.strftime('%b %d, %Y')


@app.template_filter('toHex')
def to_hex(data: str):
    data = data.encode('ascii').hex()
    return f'0x{data}'


@app.template_filter('toDuration')
def to_duration(seconds: Union[int, float]):
    duration = str(dt.timedelta(seconds=int(seconds)))
    if duration[:3] == '0:0':
        duration = duration[3:]
    elif duration[:2] == '0:':
        duration = duration[2:]
    return duration


@app.template_filter('toWei')
def to_hex(amount: int):
    from eth_utils import to_wei
    return to_wei(amount, 'ether')


@app.template_filter('fileSize')
def file_size(size: int):
    return maya.humanize.naturalsize(size, gnu=True)


def is_owner(user_id):
    return current_user.is_authenticated and current_user.id == user_id


if __name__ == '__main__':
    pass
