from flask import Blueprint, render_template, request

blueprint = Blueprint('routes', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        # For now, just add it to data
        data = url
        return render_template('index.html', data=data)

    # Landing page
    return render_template('index.html')
