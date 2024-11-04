# models.py
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

db = SQLAlchemy()
# migrate = Migrate()

class Lengua(db.Model):
    __tablename__ = 'lengua'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    isocode = db.Column(db.String(10), nullable=True)
    glottocode = db.Column(db.String(10), nullable=True)
    ejemplos = db.relationship('Ejemplo', backref='lengua', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'isocode': self.isocode,
            'glottocode': self.glottocode,
            'activo': self.activo
        }


class Modelo(db.Model):
    __tablename__ = 'modelo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)  # "real" for human-created examples
    endpoint = db.Column(db.String, nullable=True)  # URL for API if model-generated
    ejemplos = db.relationship('Ejemplo', backref='modelo', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)

class Ejemplo(db.Model):
    __tablename__ = 'ejemplo'
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    referencia = db.Column(db.Text, nullable=True) # Si es que se quiere mostrar el prompt o contexto
    lengua_id = db.Column(db.Integer, db.ForeignKey('lengua.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

class Experimento(db.Model):
    __tablename__ = 'experimento'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String, nullable=False, unique=True)
    nombre = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    lengua_id = db.Column(db.Integer, db.ForeignKey('lengua.id'), nullable=False)
    num_expertos = db.Column(db.Integer, nullable=False)
    num_nativos = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    lengua = db.relationship('Lengua', backref='experimentos')
    ejemplos = db.relationship('Experimento_X_Ejemplo', backref='experimento', lazy=True)
    validaciones = db.relationship('Validacion', backref='experimento', lazy=True)
    metricas = db.relationship('Metrica', secondary='experimento_metrica', lazy='subquery',
                                 backref=db.backref('experimentos', lazy=True))

class Metrica(db.Model):
    __tablename__ = 'metrica'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tipoValor = db.Column(db.String, nullable=False)  # "int", "float", "bool"
    valorMin = db.Column(db.Float, nullable=True)
    valorMax = db.Column(db.Float, nullable=True)
    tooltip = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    puntuaciones = db.relationship('PuntuacionMetrica', backref='metrica', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipoValor': self.tipoValor,
            'valorMin': self.valorMin,
            'valorMax': self.valorMax,
            'tooltip': self.tooltip,
            'activo': self.activo
        }
    
experimento_metrica = db.Table('experimento_metrica',
    db.Column('experimento_id', db.Integer, db.ForeignKey('experimento.id'), primary_key=True),
    db.Column('metrica_id', db.Integer, db.ForeignKey('metrica.id'), primary_key=True)
)

class Experimento_X_Ejemplo(db.Model):
    __tablename__ = 'experimento_x_ejemplo'
    id = db.Column(db.Integer, primary_key=True)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    ejemplo_id = db.Column(db.Integer, db.ForeignKey('ejemplo.id'), nullable=False)

    ejemplo = db.relationship('Ejemplo')
    activo = db.Column(db.Boolean, nullable=False, default=True)


class Validador(db.Model):
    __tablename__ = 'validador'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)

    # Progress tracking
    validaciones = db.relationship('Validacion', backref='validador', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)


class Validacion(db.Model):
    __tablename__ = 'validacion'
    id = db.Column(db.Integer, primary_key=True)
    ejemplo_id = db.Column(db.Integer, db.ForeignKey('ejemplo.id'), nullable=False)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    validador_id = db.Column(db.Integer, db.ForeignKey('validador.id'), nullable=False)

    puntuaciones = db.relationship('PuntuacionMetrica', backref='validacion', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)



class PuntuacionMetrica(db.Model):
    __tablename__ = 'puntuacion_metrica'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)  # Score from the evaluator
    validacion_id = db.Column(db.Integer, db.ForeignKey('validacion.id'), nullable=False)
    metrica_id = db.Column(db.Integer, db.ForeignKey('metrica.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
