import pandas as pd
import numpy as np
import re

def etapa_preprocesamiento(textos):
    #Textos es una columna de un dataframe
    #1. Pasar a minúsculas
    textos = textos.str.lower()
    #2. Eliminar caracteres especiales
    textos = textos.apply(lambda x: re.sub(r"[\W\d_]+", " ", x))

    return 

def etapa_aumentacion(textos):
    return 

def etapa_vectorizacion(textos):
    return

def pipeline(textos):
    etapa_preprocesamiento(textos)
    etapa_aumentacion(textos)
    etapa_vectorizacion(textos)
    return textos