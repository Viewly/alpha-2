from flask import (
    Blueprint,
    render_template,
)
from flask_security import (
    login_required,
)

channel = Blueprint(
    'channel',
    __name__,
    template_folder='templates'
)


@channel.route('/create')
@login_required
def channel_create():
    return render_template(
        'create.html',
    )


@channel.route('/create', methods=['POST'])
@login_required
def channel_create_api():
    pass


# SHOW A CHANNEL
# todo, move this /c/channel_id
@channel.route('/display')
def channel_display():
    return render_template(
        'display.html',
    )

# LIST MY CHANNELS
# todo: this is in /profile/edit now
