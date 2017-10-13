import datetime as dt

from flask import (
    render_template,
    request,
)
from flask_security import (
    login_required,
)
from funcy.seqs import last

from . import app, mongo
from .methods import (
    despam_results,
    route,
    Projection,
)


# router
# ------
@app.route('/')
def index():
    return trending_videos(page_num=0)


@app.route('/new')
def new_videos(page_num=0):
    items_per_page = 20
    page_num = page_num or int(request.args.get('page', 0))

    videos = despam_results(mongo.db['Posts'].find(
        filter={},
        projection=Projection.light(),
        sort=[('created', -1)],
        limit=items_per_page,
        skip=items_per_page * page_num,
    ))
    return render_template(
        'new.html',
        videos=videos,
        page_num=page_num,
    )


@app.route('/trending')
def trending_videos(page_num=0):
    items_per_page = 20
    page_num = page_num or int(request.args.get('page', 0))

    past_date = dt.datetime.now() - dt.timedelta(days=4)
    filter_condition = {
        'created': {'$gt': past_date},
        'pending_payout_value.amount': {'$gt': 2},
    }
    videos = despam_results(mongo.db['Posts'].find(
        filter=filter_condition,
        projection=Projection.light(),
        sort=[('pending_payout_value.amount', -1)],
        limit=items_per_page,
        skip=items_per_page * page_num,
    ))
    return render_template(
        'trending.html',
        videos=videos,
        page_num=page_num,
    )


@app.route('/embed/<permlink>', methods=['GET'])
def embed(permlink):
    meta = mongo.db['Posts'].find_one_or_404(
        {'permlink': permlink},
        {'json_metadata': 1}
    )['json_metadata']

    return render_template(
        'embed.html',
        video_obj=meta['video'],
        img_obj=meta['img'],
        ipfs_url=app.config['ipfs.gateway'],
        autoPlay=request.args.get('autoPlay', False),
    )


@app.route('/embed_steem/<author>/<permlink>', methods=['GET'])
def embed_steem(author, permlink):
    return render_template(
        'embed_steem.html',
        author=author,
        permlink=permlink,
        ipfs_url=app.config['ipfs.gateway'],
        autoPlay=request.args.get('autoPlay', False),
    )


@app.route('/view/<author>/<permlink>', methods=['GET'])
def view(author, permlink):
    video = mongo.db['Posts'].find_one_or_404({
        'author': author,
        'permlink': permlink
    })
    return render_template(
        'view.html',
        video=video,
    )


@app.route('/v/<string:permlink>', methods=['GET'])
def view_p(permlink):
    video = mongo.db['Posts'].find_one_or_404({
        'permlink': permlink
    })
    return render_template(
        'view.html',
        video=video,
    )


@app.route('/ipfs/<string:root_hash>', methods=['GET'])
def view_h(root_hash):
    video = mongo.db['Posts'].find_one_or_404({
        'json_metadata.video.root': root_hash,
    })
    return render_template(
        'view.html',
        video=video,
    )


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = despam_results(route(mongo, query))
    return render_template(
        'search.html',
        results=results,
        query=query,
    )


@app.route('/secret', methods=['GET'])
@login_required
def secret():
    return "hi there"


# template helpers
# ----------------
@app.context_processor
def utility_processor():
    def ipfs_location(root_hash, filename):
        return "%s/ipfs/%s/%s" % (app.config['ipfs.gateway'], root_hash, filename)

    def block_num():
        return mongo.db['settings'].find_one().get('last_block', 0)

    return dict(
        ipfs_location=ipfs_location,
        block_num=block_num,
        virtual_host=lambda: app.config['VIRTUAL_HOST'].rstrip('/'),
        uploader_uri=lambda: app.config['UPLOADER_URI'].rstrip('/'),
    )


@app.template_filter('scProfilePic')
def profile_pic(username):
    return "https://img.steemconnect.com/@%s?s=72" % username


@app.template_filter('humanDate')
def human_date(dto: dt.datetime):
    return dto.strftime('%b %d, %Y')


@app.template_filter('stripPreview')
def strip_preview(content):
    return last(content.split('>Viewly</a></center><br>', maxsplit=1))


@app.template_filter('uniqueTags')
def unique_tags(tags):
    return list(set(map(str.lower, tags)) - {'viewly'})


if __name__ == '__main__':
    pass
