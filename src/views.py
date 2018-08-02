import datetime as dt
import json
from typing import Union

import maya
from flask import (
    render_template,
    request,
    jsonify,
    abort,
    redirect,
    url_for,
)
from flask_security import (
    current_user,
    login_required,
)
from sqlalchemy import desc, func

from . import app, db
from .core.html import html2text, markdown2html
from .disqus import (
    get_disqus_sso,
    get_disqus_user,
)
from .methods import (
    guess_thumbnail_cdn_url,
    guess_avatar_cdn_url,
    guess_timeline_cdn_url,
)
from .models import (
    Video,
    Channel,
    TranscoderJob,
    Follow,
    Vote,
    User,
    Reward,
)


# router
# ------
@app.route('/')
def index():
    return redirect(url_for('new'))


@app.route('/v/<string:video_id>', methods=['GET'])
def view_video(video_id):
    video = Video.query.filter_by(id=video_id).first_or_404()
    if not video.published_at and not is_owner(video.user_id):
        return abort(404)

    t = int(request.args.get('t', 0))
    timer = f"&t={t}" if t else ''
    return render_template('view.html', video=video, timer=timer)


@app.route('/embed/<string:video_id>', methods=['GET'])
def embed(video_id):
    player_cdn = app.config['PLAYER_URL']
    return redirect(f"{player_cdn}/?videoId={video_id}&autoPlay=true&hideLogo=true")


@app.route('/c/<string:channel_id>', methods=['GET'])
def view_channel(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    videos = \
        Video.query.filter_by(channel_id=channel_id).order_by(desc(Video.published_at))

    # do not show unpublished videos to public
    if not is_owner(channel.user_id):
        videos = videos.filter(Video.published_at.isnot(None))

    follower_count = Follow.query.filter_by(channel_id=channel.id).count()

    return render_template(
        'channel.html',
        channel=channel,
        videos=videos.limit(30).all(),
        follower_count=follower_count,
        s3_bucket_name=app.config['S3_UPLOADS_BUCKET'],
        s3_bucket_region=app.config['S3_UPLOADS_REGION'],
        s3_user_access_key=app.config['S3_UPLOADER_PUBLIC_KEY'],
    )


@app.route('/search', methods=['GET'])
def search(page_num=0, items_per_page=18):
    limit = items_per_page
    page_num = page_num or int(request.args.get('page', 0))

    search_query = request.args.get('q')
    q = """
    SELECT v.id, v.title,
           v.description,
           v.video_metadata,
           v.published_at,
           v.is_nsfw,
           c.display_name AS channel_name, c.id AS channel_id
    FROM video v LEFT JOIN channel c
    ON v.channel_id = c.id
    WHERE to_tsvector(v.title || ' ' || v.description) @@ plainto_tsquery(:search)
     AND v.published_at IS NOT NULL
     AND v.analyzed_at IS NOT NULL
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
              .filter(Video.published_at.isnot(None),
                      Video.analyzed_at.isnot(None),
                      Video.is_nsfw.is_(False))
              .order_by(desc(Video.published_at))
              .limit(limit).offset(limit * page_num).all())

    return render_template(
        'videos.html',
        section_title='New Videos',
        videos=videos,
        page_num=page_num,
        items_per_page=items_per_page,
    )


@app.route('/trending', methods=['GET'])
def trending(page_num=0, items_per_page=18):
    """
    select * from video
    join lateral (
        select sum((token_amount + delegated_amount) * weight) as score
        from vote
        where created_at > (now() - interval '7 days')
          and vote.video_id = video.id
        group by video_id) vote_sum on (true)
    where score > 0
      and analyzed_at is not null
      and is_nsfw = false
    order by score desc
    limit 10;
    """
    limit = items_per_page
    page_num = page_num or int(request.args.get('page', 0))

    most_voted = \
        (db.session.query(
            Vote.video_id,
            func.sum((Vote.token_amount + Vote.delegated_amount) * Vote.weight)
                .label('weight'))
         .filter("created_at > (now() - interval '7 days')")
         .group_by(Vote.video_id)
         .subquery())

    videos = \
        (db.session.query(Video)
         .join(most_voted)
         .filter(Video.published_at.isnot(None),
                 Video.analyzed_at.isnot(None),
                 Video.is_nsfw.is_(False),
                 'weight > 0')
         .order_by(desc('weight'))
         .limit(limit)
         .offset(limit * page_num)
         .all())

    return render_template(
        'videos.html',
        section_title='Trending Videos',
        videos=videos,
        page_num=page_num,
        items_per_page=items_per_page,
    )


@app.route('/feed', methods=['GET'])
@login_required
def feed(page_num=0, items_per_page=18):
    limit = items_per_page
    page_num = page_num or int(request.args.get('page', 0))

    following = db.session.query(Follow.channel_id). \
        filter_by(user_id=current_user.id).subquery()
    videos = (db.session.query(Video)
              .filter(Video.published_at.isnot(None),
                      Video.channel_id.in_(following))
              .order_by(desc(Video.published_at))
              .limit(limit).offset(limit * page_num).all())

    return render_template(
        'videos.html',
        section_title='Your Feed',
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
    channels = \
        (db.session.query(
            Channel,
            func.count(Video.id).label('video_count'),
            func.sum(Reward.creator_reward).label('creator_rewards'))
         .outerjoin(Video)
         .outerjoin(Reward)
         .group_by(Channel)
         .having(Channel.user_id == current_user.id)
         .order_by(desc('video_count')))
    return render_template(
        'edit_profile.html',
        channels=channels,
    )


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/wallet')
@app.route('/wallet/generate')
@app.route('/wallet/<string:address>')
def wallet(address = ''):
    return render_template('wallet.html')

@app.route('/token')
def token_page():
    return render_template('token.html')


@app.route('/token/info', methods=['GET'])
def token_info():
    from .core.eth import view_token_supply
    token = dict(
        symbol='VIEW',
        name='view.ly',
        tokenAddress=app.config['VIEW_TOKEN_ADDRESS'],
        maxSupply=100_000_000,
        currentSupply=int(view_token_supply()),
    )
    return jsonify(**token)


@app.route('/_/stats')
@login_required
def stats():
    videos = Video.query.count()
    published_videos = Video.query.filter(Video.published_at.isnot(None)).count()
    nsfw_videos = Video.query.filter(Video.is_nsfw.is_(True)).count()
    pending_analysis = Video.query.filter(Video.analyzed_at.is_(None)).count()

    users = User.query.count()
    q_recent_login = """
    current_login_at is not null and current_login_at > (now() - interval '30 days')
    """
    active_users = User.query.filter(q_recent_login).count()
    unconfirmed_users = User.query.filter(User.confirmed_at.is_(None)).count()

    channels = Channel.query.count()
    channels_w_videos = Video.query.distinct(Video.channel_id).count()
    channels_w_published_videos = (
        Video.query
            .filter(Video.published_at.isnot(None))
            .distinct(Video.channel_id)
            .count()
    )

    return render_template(
        'stats.html',
        videos=videos,
        published_videos=published_videos,
        nsfw_videos=nsfw_videos,
        pending_analysis=pending_analysis,
        users=users,
        active_users=active_users,
        unconfirmed_users=unconfirmed_users,
        channels=channels,
        channels_w_videos=channels_w_videos,
        channels_w_published_videos=channels_w_published_videos,
    )


@app.route('/auth_token', methods=['GET'])
@login_required
def auth_token():
    return jsonify({'auth_token': current_user.get_auth_token()})


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


if app.config['IS_PRODUCTION']:
    @app.errorhandler(500)
    def internal_server_error(_):
        return render_template('500.html'), 500

auth_token_cache = dict()


def get_auth_token_cached(current_user):
    """ Cache users tokens. If token is less then 15 min away from expiry, expired or
    not in cache, generate a fresh auth token.

    # todo
    Note: This method is a hack. Replace it with encrypted, auto-expiring redis cache
    as soon as the redis cluster is deployed.

    Faults:
     - will only work if user is served from precisely this server && instance
     - will cause memory leaks if not pruned every once in a while
    """
    global auth_token_cache

    if not current_user or not current_user.is_authenticated:
        return

    def _has_expired(dto: dt.datetime) -> bool:
        return dto < dt.datetime.now()

    cache = auth_token_cache.get(current_user.id)
    if (cache and _has_expired(cache[1])) or not cache:
        expiry_time = dt.datetime.now() + dt.timedelta(
            seconds=(app.config['SECURITY_TOKEN_MAX_AGE'] - 900))
        auth_token_cache[current_user.id] = \
            (current_user.get_auth_token(), expiry_time)

    return auth_token_cache[current_user.id][0]


# template helpers
# ----------------
@app.context_processor
def utility_processor():
    from .core.eth import gas_price

    def block_num():
        return 0

    def get_transcoding_status(video_id: str):
        job = TranscoderJob.query.filter_by(
            video_id=video_id,
            preset_type='fallback').first()
        if job:
            return job.status.name
        return 'pending'

    def description2text(description):
        try:
            return html2text(markdown2html(description))
        except:
            return ''

    def can_vote(publish_dto) -> bool:
        if not publish_dto:
            return False
        publish_dto = publish_dto.replace(tzinfo=None)
        deadline = publish_dto + dt.timedelta(days=app.config['DISTRIBUTION_GAME_DAYS'])
        return deadline > dt.datetime.utcnow()

    return dict(
        block_num=block_num,
        get_transcoding_status=get_transcoding_status,
        description2text=description2text,
        get_disqus_sso=get_disqus_sso,
        get_disqus_user=get_disqus_user,
        guess_thumbnail_cdn_url=guess_thumbnail_cdn_url,
        guess_avatar_cdn_url=guess_avatar_cdn_url,
        guess_timeline_cdn_url=guess_timeline_cdn_url,
        virtual_host=lambda: app.config['VIRTUAL_HOST'].rstrip('/'),
        cdn_url=lambda: app.config['CDN_URL'],
        player_url=lambda: app.config['PLAYER_URL'],
        eth_chain=lambda: app.config['ETH_CHAIN'],
        gas_price=gas_price,
        view_token_abi=lambda: json.dumps(app.config['VIEW_TOKEN_ABI']),
        video_publisher_abi=lambda: json.dumps(app.config['VIDEO_PUBLISHER_ABI']),
        view_token_address=lambda: app.config['VIEW_TOKEN_ADDRESS'],
        video_publisher_address=lambda: app.config['VIDEO_PUBLISHER_ADDRESS'],
        voting_power_delegator_address=lambda: app.config['VOTING_POWER_DELEGATOR_ADDRESS'],
        voting_power_delegator_abi=lambda: json.dumps(app.config['VOTING_POWER_DELEGATOR_ABI']),
        get_auth_token_cached=get_auth_token_cached,
        can_vote=can_vote,
        nsfw_cover_img='https://i.imgur.com/kXBgFBy.png',
        avatar_fallback='https://i.imgur.com/32AwiVw.jpg',
        cover_fallback='https://i.imgur.com/04kFE8B.png',
    )


@app.template_filter('readableNumber')
def readable_number(number):
    if type(number) != int:
        return number
    return format(number, ',d')


@app.template_filter('humanDate')
def human_date(dto: dt.datetime):
    if not dto:
        return ''
    if type(dto) == str:
        dto = maya.parse(dto).datetime()
    return dto.strftime('%b %d, %Y')


@app.template_filter('ageDate')
def age_date(dto: dt.datetime):
    if not dto:
        return ''
    if type(dto) == str:
        m = maya.parse(dto)
    elif type(dto) == dt.datetime:
        m = maya.MayaDT.from_datetime(dto)
    else:
        raise NotImplementedError(
            f'Date {dto} is of unsupported type')
    return m.slang_time()


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
