# api.py
from flask import Blueprint, request, jsonify
from models import db, Lengua, Modelo, Ejemplo, Experimento, Experimento_X_Ejemplo, Metrica, Validacion

api = Blueprint('api', __name__, url_prefix='/api')  # Prefix all routes with /api

@api.route('/add_experiment', methods=['POST'])
def add_experiment():
    data = request.json
    experiment = Experimento(language_id=data['language_id'], name=data['name'])
    db.session.add(experiment)
    db.session.commit()
    return jsonify({"message": "Experiment created", "experiment_id": experiment.id})

@api.route('/validate_example', methods=['POST'])
def validate_example():
    data = request.json
    validation = Validacion(
        experiment_example_id=data['experiment_example_id'],
        validator_id=data['validator_id'],
        score=data['score']
    )
    db.session.add(validation)
    db.session.commit()
    return jsonify({"message": "Validation recorded", "validation_id": validation.id})

@api.route('/lenguas', methods=['GET'])
def get_lenguas():
    lenguas = Lengua.query.all()
    return jsonify([lengua.serialize() for lengua in lenguas])

@api.route('/lenguas', methods=['POST'])
def add_lengua():
    data = request.json
    lengua = Lengua(name=data['name'])
    db.session.add(lengua)
    db.session.commit()
    return jsonify({"message": "Language added", "language_id": lengua.id})