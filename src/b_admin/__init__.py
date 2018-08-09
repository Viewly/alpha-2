import datetime as dt

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
)
from flask_security import (
    login_required,
    roles_required,
)
from flask_wtf import FlaskForm
from funcy import first
from sqlalchemy import desc
from wtforms import IntegerField
from wtforms.validators import DataRequired

from .. import db
from ..models import DistributionSettings

admin = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
)


class DistributionSettingsForm(FlaskForm):
    creator_rewards_pool = IntegerField(
        'Creator rewards pool',
        validators=[
            DataRequired(),
        ]
    )
    voter_rewards_pool = IntegerField(
        'Voter rewards pool',
    )
    votes_per_user = IntegerField(
        'Votes per user',
        validators=[
            DataRequired(),
        ]
    )
    min_reward = IntegerField(
        'Minimum reward',
        validators=[
            DataRequired(),
        ]
    )


@admin.route('/distribution_settings', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def distribution_settings():
    error = None
    form = DistributionSettingsForm()

    entries = db.session.query(DistributionSettings).order_by(
        desc(DistributionSettings.id),
    ).limit(25).all()

    last_entry = first(entries)

    if last_entry:
        if not form.creator_rewards_pool.data:
            form.creator_rewards_pool.data = last_entry.creator_rewards_pool
        if not form.voter_rewards_pool.data:
            form.voter_rewards_pool.data = last_entry.voter_rewards_pool
        if not form.votes_per_user.data:
            form.votes_per_user.data = last_entry.votes_per_user
        if not form.min_reward.data:
            form.min_reward.data = last_entry.min_reward

    if form.validate_on_submit():
        setting = DistributionSettings(
            creator_rewards_pool=int(form.creator_rewards_pool.data),
            voter_rewards_pool=int(form.voter_rewards_pool.data),
            votes_per_user=int(form.votes_per_user.data),
            min_reward=int(form.min_reward.data),
            created_at=dt.datetime.utcnow()
        )
        db.session.add(setting)
        db.session.commit()
        return redirect(url_for('.distribution_settings'))

    return render_template(
        'distribution_settings.html',
        form=form,
        error=error,
        entries=entries,
    )
