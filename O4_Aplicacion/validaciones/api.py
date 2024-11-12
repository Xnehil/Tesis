# api.py
from flask import Blueprint, request, jsonify, render_template
from models import db, Lengua, Modelo, Ejemplo, Experimento, Experimento_X_Ejemplo, Metrica, Validacion, Validador, PuntuacionMetrica
import random 
import uuid


api = Blueprint('api', __name__, url_prefix='/api')  # Prefix all routes with /api

@api.route('/crear-experimento', methods=['POST'])
def crear_experimento():
    try:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        language_id = request.form.get('language')
        archivos = request.files.getlist('archivos[]')
        metrics = request.form.getlist('metrics[]')
        num_native = request.form.get('num_native')
        num_experts = request.form.get('num_experts')

        print(f"Nombre: {nombre}")
        print(f"Descripcion: {descripcion}")
        print(f"Language: {language_id}")
        print(f"Metrics: {metrics}")
        print(f"Num Native: {num_native}")
        print(f"Num Experts: {num_experts}")

        lengua = Lengua.query.get(language_id)

        #Pasos:
        # 1. Crear el experimento
        experimento = Experimento(
            nombre=nombre,
            descripcion=descripcion,
            lengua_id=language_id,
            num_expertos=num_experts,
            num_nativos=num_native,
            codigo = lengua.glottocode + str(uuid.uuid4())[:8]
        )
        db.session.add(experimento)
        db.session.flush()
        print(f"Experimento creado: {experimento.id}")
        # 2. Guardar modelos
        modelos = []
        for archivo in archivos:
            modelo = Modelo(
                nombre=archivo.filename.split('.')[0],
                experimento_id=experimento.id
            )
            db.session.add(modelo)
            modelos.append(modelo)
        db.session.flush()
        print(f"Modelos guardados: {len(modelos)}")
        # 3. Guardar ejemplos
        ejemplos = []
        for i, archivo in enumerate(archivos):
            modelo = modelos[i]
            lines = archivo.read().decode('utf-8').split('\n')
            lines = [line for line in lines if line.strip()]
            percentage = request.form.get(f'percentage_{i}')
            if percentage:
                n = int(len(lines) * float(percentage) / 100)
                lines = random.sample(lines, n)
            for line in lines:
                ejemplo = Ejemplo(
                    contenido=line,
                    lengua_id=language_id,
                    modelo_id=modelo.id
                )
                ejemplos.append(ejemplo)
            print(f"Modelo {i}: {modelo.id} - {modelo.nombre} - {len(lines)} ejemplos")
        db.session.add_all(ejemplos)
        db.session.flush()  # Ensure ejemplo.id is available

        # Create Experimento_X_Ejemplo instances
        exp_ejemplos = []
        for ejemplo in ejemplos:
            print(f"Ejemplo {ejemplo.id}")
            exp_ejemplos.append(Experimento_X_Ejemplo(
                experimento_id=experimento.id,
                ejemplo_id=ejemplo.id
            ))
        db.session.add_all(exp_ejemplos)
        print(f"Todos los ejemplos guardados")
        
        # 4. Guardar metricas
        for metric_id in metrics:
            experimento.metricas.append(Metrica.query.get(metric_id))

        # 5. Guardar validadores
        validadores = []
        for i in range(int(num_experts)):
            validador = Validador(
                experimento_id=experimento.id,
                tipo='expert',
                url = str(uuid.uuid4())
            )
            validadores.append(validador)
        for i in range(int(num_native)):
            validador = Validador(
                experimento_id=experimento.id,
                tipo='native',
                url = str(uuid.uuid4())
            )
            validadores.append(validador)
        db.session.add_all(validadores)
        print(f"Validadores guardados")
        db.session.commit()
        for validador in validadores:
            for ejemplo in ejemplos:
                crear_validacion(validador, experimento, ejemplo, experimento.metricas, crearPuntuaciones=True)
        print(f"Validaciones creadas")
        return jsonify({"message": "Experimento creado exitosamente", "experimento_cod": experimento.codigo}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


def crear_validacion(validador, experimento, ejemplo, metricas, crearPuntuaciones=False):
    print(f"Creando validacion para {validador.id} - {experimento.id} - {ejemplo.id}")
    validacion = Validacion(
        validador_id=validador.id,
        experimento_id=experimento.id,
        ejemplo_id=ejemplo.id
    )
    db.session.add(validacion)
    db.session.commit()
    if crearPuntuaciones:
        puntuaciones = []
        for metrica in metricas:
            puntuacion = PuntuacionMetrica(
                validacion_id=validacion.id,
                metrica_id=metrica.id,
                valor=None
            )
            puntuaciones.append(puntuacion)
        db.session.bulk_save_objects(puntuaciones)
        db.session.commit()
    return validacion

@api.route('/lenguas', methods=['GET'])
def get_lenguas():
    lenguas = Lengua.query.filter_by(activo=True).all()
    if request.args.get('html') == 'true':
        options_html = ''.join([f'<option value="{lengua.id}"><strong>{lengua.nombre}</strong> - {lengua.isocode or lengua.glottocode}</option>' for lengua in lenguas])
        return options_html
    return jsonify([lengua.serialize() for lengua in lenguas])

@api.route('/lenguas', methods=['POST'])
def add_lenguas():
    data = request.json
    if not isinstance(data, list):
        data = [data]
    for item in data:
        lengua = Lengua(
            nombre=item['nombre'],
            isocode=item.get('isocode'),
            glottocode=item.get('glottocode')
        )
        db.session.add(lengua)
    db.session.commit()
    return jsonify({"message": "Languages added"}), 201

@api.route('/lenguas/<int:lengua_id>', methods=['PUT'])
def update_lengua(lengua_id):
    data = request.json
    lengua = Lengua.query.get_or_404(lengua_id)
    lengua.nombre = data.get('nombre', lengua.nombre)
    lengua.isocode = data.get('isocode', lengua.isocode)
    lengua.glottocode = data.get('glottocode', lengua.glottocode)
    db.session.commit()
    return jsonify({"message": "Language updated"})

@api.route('/lenguas/<int:lengua_id>', methods=['DELETE'])
def delete_lengua(lengua_id):
    lengua = Lengua.query.get_or_404(lengua_id)
    lengua.activo = False
    db.session.commit()
    return jsonify({"message": "Language deleted"})

@api.route('/metricas', methods=['GET'])
def get_metricas():
    metricas = Metrica.query.filter_by(activo=True).all()
    return jsonify([metrica.serialize() for metrica in metricas])

@api.route('/metricas', methods=['POST'])
def add_metricas():
    data = request.json
    if not isinstance(data, list):
        data = [data]
    for item in data:
        metrica = Metrica(
            nombre=item['nombre'],
            descripcion=item.get('descripcion'),
            tipoValor=item['tipoValor'],
            valorMin=item.get('valorMin'),
            valorMax=item.get('valorMax'),
            tooltip=item['tooltip']
        )
        db.session.add(metrica)
    db.session.commit()
    return jsonify({"message": "Metrics added"}), 201

@api.route('/metricas/<int:metrica_id>', methods=['PUT'])
def update_metrica(metrica_id):
    data = request.json
    metrica = Metrica.query.get_or_404(metrica_id)
    metrica.nombre = data.get('nombre', metrica.nombre)
    metrica.descripcion = data.get('descripcion', metrica.descripcion)
    metrica.tipoValor = data.get('tipoValor', metrica.tipoValor)
    metrica.valorMin = data.get('valorMin', metrica.valorMin)
    metrica.valorMax = data.get('valorMax', metrica.valorMax)
    metrica.tooltip = data.get('tooltip', metrica.tooltip)
    db.session.commit()
    return jsonify({"message": "Metric updated"})

@api.route('/experimento/<string:experimento_cod>', methods=['GET'])
def get_experimento(experimento_cod):
    experimento = Experimento.query.filter_by(codigo=experimento_cod).first()
    if not experimento:
        return jsonify({"message": "Experiment not found"}), 404
    return jsonify(experimento.serialize())

@api.route('/experimentos', methods=['GET'])
def get_experimentos():
    experimentos = Experimento.query.all()
    return jsonify([experimento.serialize() for experimento in experimentos])

@api.route('/validador/<string:validador_id>', methods=['PUT', 'POST'])
def update_validador(validador_id):
    try:
        data = request.json
        validador = Validador.query.get_or_404(validador_id)
        validador.url = data.get('url', validador.url)
        validador.activo = data.get('activo', validador.activo)
        validador.nombre = data.get('nombre', validador.nombre)
        validador.contacto = data.get('contacto', validador.contacto)
        db.session.commit()
        return jsonify({"message": "Validador updated"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    