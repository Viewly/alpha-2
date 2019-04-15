from flask import (
    Blueprint,
    render_template,
)
from sqlalchemy import desc, func, or_, text

from .. import db
from ..models import (
    Video,
    Vote,
    GamePeriod,
    Reward,
)

game = Blueprint(
    'game',
    __name__,
    template_folder='templates'
)


@game.route('/')
def index():
    q = """
    SELECT *, rewards/videos AS rpv
     FROM top_creators_30_days
     ORDER BY rewards DESC
     LIMIT :limit;
    """
    rs = db.session.execute(q, {
        "limit": 10,
    })
    leaderboard = [dict(zip(rs.keys(), item)) for item in rs.fetchall()]

    return render_template(
        'index.html',
        leaderboard=leaderboard
    )


@game.route('/periods')
def list_periods():
    periods = \
        (db.session.query(GamePeriod)
         .order_by(desc(GamePeriod.end))
         .limit(1000)
         .all())

    return render_template(
        'periods.html',
        periods=periods,
    )


@game.route('/rewards')
def list_rewards():
    rewards = \
        (db.session.query(Reward)
         .filter_by(creator_payable=True)
         .order_by(desc(Reward.period_id))
         .limit(1000)
         .all())

    return render_template(
        'rewards.html',
        rewards=rewards,
    )


@game.route('/period/<int:period_id>')
def period_rewards(period_id):
    period = db.session.query(GamePeriod).filter_by(id=period_id).one()

    rewards_summary = \
        (db.session.query(
            Reward.video_id,
            func.count(Reward.id),
            func.sum(Reward.creator_reward).label('creator_rewards'),
            func.sum(Reward.voter_reward))
         .filter_by(period_id=period_id)
         .group_by(Reward.video_id)
         .order_by(text("creator_rewards desc"))
         .all())

    rewards = \
        (db.session.query(Reward, Vote)
         .filter_by(period_id=period_id)
         .from_self()
         .join(Vote, Vote.id == Reward.vote_id)
         .order_by(desc(Reward.creator_reward))
         .all())

    return render_template(
        'period_rewards.html',
        period=period,
        rewards=rewards,
        rewards_summary=rewards_summary,
    )


@game.route('/payment/<string:txid>')
def explain_payment(txid):
    rewards = \
        (db.session.query(Reward)
         .filter(or_(Reward.creator_txid == txid, Reward.voter_txid == txid))
         .order_by(desc(Reward.period_id))
         .all())

    return render_template(
        'payment.html',
        txid=txid,
        rewards=rewards,
    )


@game.route('/votes/<string:video_id>')
def video_votes(video_id: str):
    video = db.session.query(Video).filter_by(id=video_id).one()

    votes = \
        (db.session.query(Vote)
         .filter_by(video_id=video_id)
         .order_by(desc(Vote.token_amount))
         .all())

    rewards = \
        (db.session.query(Reward, Vote)
         .filter_by(video_id=video_id)
         .join(Vote)
         .order_by(desc(Reward.creator_reward))
         .all())

    period = None
    summary = None
    if rewards:
        period_id = rewards[0][0].period_id
        period = db.session.query(GamePeriod).filter_by(id=period_id).one()
        summary = \
            (db.session.query(
                func.count(Reward.id).label('rewards_count'),
                func.sum(Reward.creator_reward).label('creator_rewards'),
                func.sum(Reward.voter_reward).label('voter_rewards'))
             .filter_by(video_id=video_id, creator_payable=True)
             .one())

    return render_template(
        'video_votes.html',
        video=video,
        votes=votes,
        rewards=rewards,
        period=period,
        summary=summary,
    )


@game.route('/voter/<string:eth_address>')
def voter_activity(eth_address: str):
    votes = \
        (db.session.query(Vote)
         .filter_by(eth_address=eth_address)
         .order_by(desc(Vote.created_at))
         .limit(100)
         .all())

    return render_template(
        'voter.html',
        eth_address=eth_address,
        votes=votes,
    )
