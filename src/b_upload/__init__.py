from flask import (
    Blueprint,
    render_template,
)

upload = Blueprint(
    'upload',
    __name__,
    template_folder='templates'
)


@upload.route('/')
def index():
    return render_template('index.html')
