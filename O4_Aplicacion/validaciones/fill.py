import csv
import requests

def fill_database(file_path, url, batch_size=25):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        batch = []
        for row in reader:
            # Remove latitud and longitud keys
            row.pop('latitud', None)
            row.pop('longitud', None)
            batch.append(row)
            if len(batch) >= batch_size:
                response = requests.post(url, json=batch)
                if response.status_code == 201:
                    print(f"Added batch of {len(batch)} languages")
                else:
                    print(f"Failed to add batch - {response.text}")
                batch = []
        # Send any remaining rows
        if batch:
            response = requests.post(url, json=batch)
            if response.status_code == 201:
                print(f"Added batch of {len(batch)} languages")
            else:
                print(f"Failed to add batch - {response.text}")

def fill_metricas(url):
    # class Metrica(db.Model):
    # __tablename__ = 'metrica'
    # id = db.Column(db.Integer, primary_key=True)
    # nombre = db.Column(db.String, nullable=False)
    # descripcion = db.Column(db.Text, nullable=True)
    # tipoValor = db.Column(db.String, nullable=False)  # "int", "float", "bool"
    # valorMin = db.Column(db.Float, nullable=True)
    # valorMax = db.Column(db.Float, nullable=True)
    # tooltip = db.Column(db.Text, nullable=False)
    # activo = db.Column(db.Boolean, nullable=False, default=True)

    # puntuaciones = db.relationship('PuntuacionMetrica', backref='metrica', lazy=True)
    metricas = [
        {
            "nombre": "Fluidez",
            "descripcion": "Mide la naturalidad de las respuestas. Responde a la pregunta, ¿el texto mostrado es natural?",
            "tipoValor": "int",
            "valorMin": 1,
            "valorMax": 5,
            "tooltip": "Elija un valor entre 1 y 5 donde 1 representa una respuesta poco natural y 5 una respuesta muy natural"
        },
        {
            "nombre": "Correctitud",
            "descripcion": "Mide qué tan correcto es gramaticalmente el texto. Responde a la pregunta, ¿el texto mostrado es gramaticalmente correcto de acuerdo a las reglas de la lengua?",
            "tipoValor": "int",
            "valorMin": 1,
            "valorMax": 5,
            "tooltip": "Elija un valor entre 1 y 5 donde 1 representa una respuesta nada correcta y 5 una respuesta muy correcta"
        },
        {
            "nombre": "Pertinencia",
            "descripcion": "Mide qué tan relevante es el texto para el experimento. En este caso, responde a la pregunta, ¿el texto mostrado pertenece a la lengua que se está evaluando?",
            "tipoValor": "bool",
            "tooltip": "Elija 'Sí' si el texto pertenece a la lengua que se está evaluando, 'No' en caso contrario"
        }
    ]

    response = requests.post(url, json=metricas)
    if response.status_code == 201:
        print(f"Added metrics")
    else:
        print(f"Failed to add metrics - {response.text}")

fill_metricas('http://localhost:5000/api/metricas')
fill_database('data/lenguasPeru.csv', 'http://localhost:5000/api/lenguas')