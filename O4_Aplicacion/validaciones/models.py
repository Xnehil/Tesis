# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lengua(db.Model):
    __tablename__ = 'lengua'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    isocode = db.Column(db.String(10), nullable=False)

    ejemplos = db.relationship('Ejemplo', backref='lengua', lazy=True)


class Modelo(db.Model):
    __tablename__ = 'modelo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)  # "real" for human-created examples
    endpoint = db.Column(db.String, nullable=True)  # URL for API if model-generated

    ejemplos = db.relationship('Ejemplo', backref='modelo', lazy=True)


class Ejemplo(db.Model):
    __tablename__ = 'ejemplo'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    lengua_id = db.Column(db.Integer, db.ForeignKey('lengua.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)


class Experimento(db.Model):
    __tablename__ = 'experimento'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String, nullable=False, unique=True)
    lengua_id = db.Column(db.Integer, db.ForeignKey('lengua.id'), nullable=False)
    num_validadores = db.Column(db.Integer, nullable=False)

    # Relationships
    lengua = db.relationship('Lengua', backref='experimentos')
    ejemplos = db.relationship('Experimento_X_Ejemplo', backref='experimento', lazy=True)
    validaciones = db.relationship('Validacion', backref='experimento', lazy=True)


class Experimento_X_Ejemplo(db.Model):
    __tablename__ = 'experimento_x_ejemplo'
    id = db.Column(db.Integer, primary_key=True)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    ejemplo_id = db.Column(db.Integer, db.ForeignKey('ejemplo.id'), nullable=False)

    ejemplo = db.relationship('Ejemplo')


class Validador(db.Model):
    __tablename__ = 'validador'
    id = db.Column(db.Integer, primary_key=True)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)

    # Progress tracking
    validaciones = db.relationship('Validacion', backref='validador', lazy=True)


class Validacion(db.Model):
    __tablename__ = 'validacion'
    id = db.Column(db.Integer, primary_key=True)
    ejemplo_id = db.Column(db.Integer, db.ForeignKey('ejemplo.id'), nullable=False)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    validador_id = db.Column(db.Integer, db.ForeignKey('validador.id'), nullable=False)

    puntuaciones = db.relationship('PuntuacionMetrica', backref='validacion', lazy=True)


class Metrica(db.Model):
    __tablename__ = 'metrica'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)

    puntuaciones = db.relationship('PuntuacionMetrica', backref='metrica', lazy=True)


class PuntuacionMetrica(db.Model):
    __tablename__ = 'puntuacion_metrica'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)  # Score from the evaluator
    validacion_id = db.Column(db.Integer, db.ForeignKey('validacion.id'), nullable=False)
    metrica_id = db.Column(db.Integer, db.ForeignKey('metrica.id'), nullable=False)
