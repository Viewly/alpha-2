import datetime as dt

import maya
from flask import (
    render_template,
    request,
    make_response,
)

from . import app
from .models import Video


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


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = []
    return render_template(
        'search.html',
        results=results,
        query=query,
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
