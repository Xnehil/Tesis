# web.py
from flask import Blueprint, render_template, send_from_directory

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return send_from_directory('static', 'index.html')

@web.route('/crear-experimento')
def crear_experimento():
    return render_template('crear-experimento.html')

@web.route('/experimento-creado')
def experimento_creado():
    return render_template('experimento-creado.html')