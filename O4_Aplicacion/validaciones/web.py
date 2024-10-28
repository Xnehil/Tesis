# web.py
from flask import Blueprint, render_template, send_from_directory

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return send_from_directory('static', 'index.html')

@web.route('/experiment/<int:experiment_id>')
def experiment_detail(experiment_id):
    # Add logic to fetch experiment details and render the template
    return render_template('experiment_detail.html', experiment_id=experiment_id)
