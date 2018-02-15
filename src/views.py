import datetime as dt

import maya
from flask import (
    render_template,
    request,
)
from flask_security import (
    current_user,
    login_required,
)
from sqlalchemy import desc

from . import app, db
from .models import Video, Channel
from .videourl import guess_thumbnail_cdn_url


# router
# ------
@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/v/<string:video_id>', methods=['GET'])
def view_video(video_id):
    video = Video.query.filter_by(id=video_id).first_or_404()
    return render_template('view.html', video=video)


@app.route('/embed/<string:video_id>', methods=['GET'])
def embed(video_id):
    from .videourl import get_video_cdn_assets

    video = Video.query.filter_by(id=video_id).first_or_404()
    return render_template(
        'embed.html',
        source=get_video_cdn_assets(video),
        autoPlay=request.args.get('autoPlay', True),
    )


@app.route('/c/<string:channel_id>', methods=['GET'])
def view_channel(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    videos = (Video.query.filter_by(channel_id=channel_id)
              .order_by(desc(Video.published_at))
              .limit(10).all())
    return render_template('channel.html', channel=channel, videos=videos)


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('q')
    q = """
    SELECT v.id, v.title, 
           c.display_name AS channel_name, c.id AS channel_id
    FROM video v LEFT JOIN channel c
    ON v.channel_id = c.id
    WHERE to_tsvector(v.title || ' ' || v.description) @@ plainto_tsquery(:search)
     AND v.published_at IS NOT NULL
    ORDER BY v.published_at DESC
    LIMIT 10;
    """
    rs = db.session.execute(q, {"search": search_query})
    results = [dict(zip(rs.keys(), item)) for item in rs.fetchall()]

    return render_template(
        'search.html',
        results=results,
        query=search_query,
    )


@app.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    return render_template(
        'edit_profile.html',
        channels=Channel.query.filter_by(user_id=current_user.id),
    )


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


# template helpers
# ----------------
@app.context_processor
def utility_processor():
    def block_num():
        return 0

    return dict(
        block_num=block_num,
        guess_thumbnail_cdn_url=guess_thumbnail_cdn_url,
        virtual_host=lambda: app.config['VIRTUAL_HOST'].rstrip('/'),
    )


@app.template_filter('humanDate')
def human_date(dto: dt.datetime):
    if not dto:
        return ''
    if type(dto) == str:
        dto = maya.parse(dto).datetime()
    return dto.strftime('%b %d, %Y')


@app.template_filter('fileSize')
def file_size(size: int):
    return maya.humanize.naturalsize(size, gnu=True)


if __name__ == '__main__':
    pass
