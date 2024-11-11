# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

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

    # Relación con experimento
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)

    def serialize(self, include_ejemplos=False):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'endpoint': self.endpoint,
            'activo': self.activo,
            'ejemplos': [ejemplo.serialize() for ejemplo in self.ejemplos] if include_ejemplos else None
        }

class Ejemplo(db.Model):
    __tablename__ = 'ejemplo'
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    referencia = db.Column(db.Text, nullable=True) # Si es que se quiere mostrar el prompt o contexto
    lengua_id = db.Column(db.Integer, db.ForeignKey('lengua.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def serialize(self, include_lengua=False, include_modelo=False):
        return {
            'id': self.id,
            'contenido': self.contenido,
            'referencia': self.referencia,
            'lengua': self.lengua.serialize() if include_lengua else None,
            'modelo': self.modelo.serialize() if include_modelo else None,
            'activo': self.activo
        }

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
    modelos = db.relationship('Modelo', backref='experimento', lazy=True)
    validadores = db.relationship('Validador', backref='experimento_rel', lazy=True)
    metricas = db.relationship('Metrica', secondary='experimento_metrica', lazy='subquery',
                                 backref=db.backref('experimentos', lazy=True))
    

    def serialize(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'lengua': self.lengua.serialize() if self.lengua else None,
            'num_expertos': self.num_expertos,
            'num_nativos': self.num_nativos,
            'activo': self.activo,
            'metricas': [metrica.serialize() for metrica in self.metricas],
            # 'ejemplos': [ejemplo.serialize() for ejemplo in self.ejemplos],
            'validadores': [validador.serialize() for validador in self.validadores],
            'modelos': [modelo.serialize(include_ejemplos=True) for modelo in self.modelos]
        }

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

    def serialize(self):
        return {
            'id': self.id,
            'experimento_id': self.experimento_id,
            'ejemplo': self.ejemplo.serialize(),
            'activo': self.activo
        }



class Validador(db.Model):
    __tablename__ = 'validador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=True)
    contacto = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    experimento = db.relationship('Experimento', backref='validadores_rel', lazy=True)

    # Progress tracking
    validaciones = db.relationship('Validacion', backref='validador', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def serialize(self, include_validaciones=False, include_experimento=False):
        return {
            'id': self.id,
            'url': self.url,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'tipo': self.tipo,
            'activo': self.activo,
            'experimento': self.experimento.serialize() if include_experimento else None,
            'validaciones': [validacion.serialize() for validacion in self.validaciones] if include_validaciones else None
        }


class Validacion(db.Model):
    __tablename__ = 'validacion'
    id = db.Column(db.Integer, primary_key=True)
    ejemplo_id = db.Column(db.Integer, db.ForeignKey('ejemplo.id'), nullable=False)
    experimento_id = db.Column(db.Integer, db.ForeignKey('experimento.id'), nullable=False)
    validador_id = db.Column(db.Integer, db.ForeignKey('validador.id'), nullable=False)

    terminado = db.Column(db.Boolean, nullable=False, default=False)
    puntuaciones = db.relationship('PuntuacionMetrica', backref='validacion', lazy=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def serialize(self, include_puntuaciones=False):
        return {
            'id': self.id,
            'ejemplo': self.ejemplo.serialize(),
            'activo': self.activo,
            'puntuaciones': [puntuacion.serialize() for puntuacion in self.puntuaciones] if include_puntuaciones else None
        }



class PuntuacionMetrica(db.Model):
    __tablename__ = 'puntuacion_metrica'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(JSON, nullable=False)
    validacion_id = db.Column(db.Integer, db.ForeignKey('validacion.id'), nullable=False)
    metrica_id = db.Column(db.Integer, db.ForeignKey('metrica.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def serialize(self):
        return {
            'id': self.id,
            'valor': self.valor,
            'activo': self.activo
        }
