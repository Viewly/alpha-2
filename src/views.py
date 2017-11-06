import datetime as dt
import maya

from flask import (
    render_template,
    request,
    make_response,
)
from flask_security import (
    login_required,
)

from . import app


# router
# ------
@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/v/<string:video_id>', methods=['GET'])
def view_video(video_id):
    return make_response('')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = []
    return render_template(
        'search.html',
        results=results,
        query=query,
    )


# template helpers
# ----------------
@app.context_processor
def utility_processor():
    def ipfs_location(root_hash, filename):
        return "%s/ipfs/%s/%s" % (app.config['ipfs.gateway'], root_hash, filename)

    def block_num():
        return 0

    return dict(
        ipfs_location=ipfs_location,
        block_num=block_num,
        virtual_host=lambda: app.config['VIRTUAL_HOST'].rstrip('/'),
        uploader_uri=lambda: app.config['UPLOADER_URI'].rstrip('/'),
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# template helpers
# ----------------
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
