import datetime as dt

from flask import (
    Blueprint,
    render_template,
    redirect,
)
from flask_security import (
    login_required,
    current_user,
)
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField
from wtforms.validators import DataRequired, Length

from .. import db
from ..models import Channel

channel = Blueprint(
    'channel',
    __name__,
    template_folder='templates'
)


class CreateChannelForm(FlaskForm):
    name = StringField(
        'Display Name for your channel',
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=25,
                message='Channel names should be 3 to 25 characters long'
            )]
    )


class EditChannelForm(CreateChannelForm):
    description = StringField(
        'A short description (70 char max)',
        validators=[
            Length(
                max=70,
                message='Channel description is too long (70 char max)'
            )]
    )


@channel.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    error = None
    form = CreateChannelForm()

    channel_count = db.session.query(Channel).filter_by(
        user_id=current_user.id,
    ).count()

    if channel_count >= 10:
        error = 'You already have 10 channels. Cannot create another one at this time.'
    else:
        if form.validate_on_submit():
            display_name = form.name.data.strip()
            chan = Channel(
                user_id=current_user.id,
                display_name=display_name,
                created_at=dt.datetime.utcnow()
            )

            if db.session.query(Channel).filter_by(
                    display_name=func.lower(display_name)).count() > 0:
                error = f'Display name "{display_name}" is already taken!'
            else:
                db.session.add(chan)
                db.session.commit()
                return redirect(f'/c/{chan.id}')

    return render_template(
        'create.html',
        form=form,
        error=error,
    )


@channel.route('/edit/<channel_id>', methods=['GET', 'POST'])
@login_required
def edit(channel_id):
    error = None
    form = EditChannelForm()

    chan = db.session.query(Channel).filter_by(id=channel_id).one()

    form.name.data = form.name.data or chan.display_name
    form.description.data = form.description.data or chan.description

    if form.validate_on_submit():
        display_name = form.name.data.strip()
        description = form.description.data.strip()
        chan.display_name = display_name
        chan.description = description

        if db.session.query(Channel).filter(
                Channel.user_id != current_user.id,
                Channel.display_name == func.lower(display_name)).count() > 0:
            error = f'Display name "{display_name}" is already taken!'
        else:
            db.session.add(chan)
            db.session.commit()
            return redirect(f'/c/{chan.id}')

    return render_template(
        'edit.html',
        form=form,
        error=error,
    )


# SHOW A CHANNEL
# todo, move this /c/channel_id
@channel.route('/display')
def channel_display():
    return render_template(
        'display.html',
    )

# LIST MY CHANNELS
# todo: this is in /profile/edit now
