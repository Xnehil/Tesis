# web.py
from flask import Blueprint, render_template, send_from_directory, request
from models import Experimento, Validador

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

@web.route('/unirse-experimento')
def unirse_experimento():
    return render_template('unirse-experimento.html')

@web.route('/validar/<string:validador_cod>')
def validar(validador_cod):
    validador = Validador.query.filter_by(url=validador_cod).first()
    if not validador:
        return render_template('error.html', message="Experiment not found"), 404
    return render_template('validar.html.j2', validador=validador.serialize(include_validaciones=True, include_experimento=True))