# web.py
from flask import Blueprint, render_template, send_from_directory, request
from models import Experimento
from api import get_experimento

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return send_from_directory('static', 'index.html')

@web.route('/crear-experimento')
def crear_experimento():
    return render_template('crear-experimento.html')

@web.route('/experimento-creado')
def experimento_creado():
    experimento_cod = request.args.get('experimento_cod')
    experimento = Experimento.query.filter_by(codigo=experimento_cod).first()
    if not experimento:
        return render_template('error.html', message="Experiment not found"), 404
    # print(experimento)
    return render_template('experimento-creado.html.j2', experimento=experimento.serialize())
