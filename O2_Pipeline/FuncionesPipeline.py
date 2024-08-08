import pandas as pd
import numpy as np
import re
import networkx as nx
import matplotlib.pyplot as plt
import random

def etapa_preprocesamiento(textos):
    #Textos es una columna de un dataframe
    #1. Pasar a minúsculas
    textos = textos.str.lower()
    #2. Eliminar caracteres especiales
    textos = textos.apply(lambda x: re.sub(r"[\W\d_]+", " ", x))

    return 

def etapa_aumentacion(textos, dict1):
    df_aumentado = pd.DataFrame(columns=['transcription', 'morpheme_break', 'pos', 'gloss_es'])
    #Cambiar sustantivos
    cambiarSustantivos(textos, dict1)
    return 


def etapa_vectorizacion(textos):
    return



def pipeline(df):
    dict1 =estructurasAuxiliares(df)

    # etapa_preprocesamiento(df['transcription'])
    etapa_aumentacion(df, dict1)
    # etapa_vectorizacion(df['transcription'])
    return dict1

def cambiarSustantivos(df, dict1, prob=0.5):
    df_aumentado = pd.DataFrame(columns=['transcription', 'morpheme_break', 'pos', 'gloss_es'])
    for index, row in df.iterrows():
        if pd.isnull(row['morpheme_break']) or pd.isnull(row['pos']) or pd.isnull(row['gloss_es']):
            continue
        morphemes, pos_tags, glosses = parse_morphemes(row)
        new_data = None
        for morpheme, pos_tag, gloss in zip(morphemes, pos_tags, glosses):
            if pos_tag == "NOUN" and np.random.rand() < prob:
                # Cambiar sustantivo
                new_data = random.choice(dict1["pos_tags"]["NOUN"])
                break
        if new_data:
            newRow=createNewRow(row, new_data, morpheme)
            print("Original: ", row)
            print("Aumentado: ", newRow)
            break



def createNewRow(row, new_data, morpheme):
    newRow = row.copy()
    #Reemplazar en row el morfema por la clave de new_data
    newRow['morpheme_break'] = newRow['morpheme_break'].replace(morpheme, new_data[0])
    #Recuperar la posición de new_data
    position = newRow['morpheme_break'].split().index(new_data[0])
    #No hace falta reemplazar en row el pos en la posición correspondiente porque sigue siendo un sustantivo
    #Reemplazar en row el gloss en la posición correspondiente
    newRow['gloss_es'] = newRow['gloss_es'].split()
    newRow['gloss_es'][position] = new_data[1]
    newRow['gloss_es'] = " ".join(newRow['gloss_es'])

    # id                  : EC-cancion.aku-2013_005
    # speaker             : Elias
    # transcription       : non kentihokobi
    # text                : non         kentihokobi
    # morpheme_break      : no   =n     kenti -hoko =bi
    # pos                 : pron =clit. n.    -suf  =clit.
    # gloss_es            : 1PL  =GEN   olla  -DIM  =ENF
    # free_translation    : nuestra ollita
    # file                : EC-cancion.aku-2013.txt
    newRow['speaker'] = newRow['speaker'] + "_augmented"
    newRow['id'] = newRow['id']+"_augmented"
    
    newRow['transcription'] = reconstructText(newRow['morpheme_break'].split())
    newRow['text']=newRow['transcription']
    return newRow

def reconstructText(morphemes):
    text = ""
    for morpheme in morphemes:
        if morpheme.startswith("="):
            text += morpheme[1:]
        elif morpheme.startswith("-"):
            text += morpheme[1:]
        else:
            if text and not text.endswith(" "):
                text += " "
            text += morpheme
    return text

def estructurasAuxiliares(df):
    #Esto devolverá dos diccionarios
    dict1 = {}
    dict2 = {} #Morfemas e info de sus pos tags y glosses
    dict3 = {} #Glosas y sus pos tags y morfemas
    dict4 = {} #Pos tags y sus morfemas y glosas
    for index, row in df.iterrows():
        if pd.isnull(row['morpheme_break']) or pd.isnull(row['pos']) or pd.isnull(row['gloss_es']):
            continue
        morphemes, pos_tags, glosses = parse_morphemes(row)
        for morpheme, pos_tag, gloss in zip(morphemes, pos_tags, glosses):
            if morpheme not in dict2:
                dict2[morpheme] = []
            if (pos_tag, gloss) not in dict2[morpheme]:
                dict2[morpheme].append((pos_tag, gloss))
            
            if gloss not in dict3:
                dict3[gloss] = []
            if (pos_tag, morpheme) not in dict3[gloss]:
                dict3[gloss].append((pos_tag, morpheme))
            
            if pos_tag not in dict4:
                dict4[pos_tag] = []
            if (morpheme, gloss) not in dict4[pos_tag]:
                dict4[pos_tag].append((morpheme, gloss))

    dict1 = {"morphemes": dict2, "glosses": dict3, "pos_tags": dict4}
    return dict1

def parse_morphemes(row):
    morphemes = row['morpheme_break'].split()
    pos_tags = [map_to_universal_tag(tag) for tag in row['pos'].split()]
    glosses = row['gloss_es'].split()
    
    return morphemes, pos_tags, glosses

def map_to_universal_tag(pos_tag):
    # Mapping for standard POS tags to Universal POS tags
    universal_map = {
        'adj': 'ADJ', 'adj.': 'ADJ',
        'adv': 'ADV', 'adv.': 'ADV', 'advv.': 'ADV', 'advv.intr': 'ADV',
        'art.': 'DET',
        'conec': 'CCONJ', 'conec.': 'CCONJ', 'conect.': 'CCONJ', 'conj.': 'CCONJ',
        'cuant.': 'NUM',
        'dem': 'DET', 'dem.': 'DET', 'demadv.': 'ADV',
        'det.': 'DET',
        'ide.': 'INTJ', 'ideo': 'INTJ', 'ideo.': 'INTJ', #ideófonos como descrito en Gramática Iskonawa 
        'int.': 'PRON', 'int.v.tran.': 'VERB', 'inter,': 'INTJ', 'inter.': 'INTJ',
        'interj.': 'INTJ', 'intj': 'INTJ', 'intj.': 'INTJ',
        'muletilla.': 'PART',
        'n': 'NOUN', 'n.': 'NOUN',
        'num': 'NUM', 'num.': 'NUM',
        'ono': 'INTJ', 'ono.': 'INTJ', 'onom.': 'INTJ',
        'pal.int': 'INTJ', 'pal.int.': 'INTJ',
        'part.': 'PART',
        'pos': 'DET', 'pos.': 'DET',
        'post': 'ADP', 'post.': 'ADP',
        'pre.': 'ADP', 'pref.-': 'ADP', 'prep.': 'ADP',
        'prom': 'PRON', 'pron': 'PRON', 'pron.': 'PRON',
        'suf.': 'PART',
        'v': 'VERB', 'v.': 'VERB', 'v.amb': 'VERB', 'v.ambi': 'VERB',
        'v.ambi.': 'VERB', 'v.int': 'VERB', 'v.intr': 'VERB', 'v.intr.': 'VERB',
        'v.tr': 'VERB', 'v.tr.': 'VERB', 'v.tran': 'VERB', 'v.tran.': 'VERB',
        '***': 'X', '-': 'PUNCT', '-***': 'X', '-adv.': 'ADV', '-lig.': 'X',
        '-n.': 'NOUN', '-suf': 'PART', '-suf.': 'PART', '-sufv.intr.': 'PART',
        '-suj.': 'PART', '-v.': 'VERB', '.': 'PUNCT', '/': 'PUNCT', ';': 'PUNCT',
        '=clit': 'PART', '=clit.': 'PART', '=clitdem': 'DET', '=clitn.': 'NOUN',
        '=clitpart.': 'PART', '=clitv.': 'VERB', '=n.': 'NOUN', '=suf.': 'PART',
        '?': 'PUNCT', 'FP': 'PART', '[...]': 'PUNCT', '[canto]': 'PART',
        '\\ps': 'X'
    }

    clitic_map = {
        'clit': 'PART',
        'clit.': 'PART',
        'clitdem': 'DET',
        'clitn.': 'NOUN',
        'clitpart.': 'PART',
        'clitv.': 'VERB'
    }
    
    if '=' in pos_tag:
        base_tag = pos_tag.split('=')[-1]
        return clitic_map.get(base_tag, 'PART')
    
    # Map the standard POS tag
    return universal_map.get(pos_tag, 'X')





