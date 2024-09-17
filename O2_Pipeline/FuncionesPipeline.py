import pandas as pd
import numpy as np
import re
import networkx as nx
import matplotlib.pyplot as plt
import random
import sentencepiece as spm

def etapa_preprocesamiento(textos, tokenizador=None):
    
    #Textos es una columna de un dataframe
    #1. Pasar a minúsculas
    textos = textos.str.lower()
    #2. Eliminar caracteres especiales
    textos = textos.apply(lambda x: re.sub(r"[\W\d_]+", " ", x))
    textos = textos.apply(lambda x: re.sub(r"ininteligible", "", x))
    #3. Eliminar espacios en blanco extra
    textos = textos.apply(lambda x: re.sub(r"\s+", " ", x))
    #4. Eliminar espacios en blanco al principio y al final
    textos = textos.str.strip()
    #5. Tokenizar usando SentencePiece
    if tokenizador:
        textos = textos.apply(lambda x: tokenizador.encode_as_pieces(x))
    return textos

def etapa_aumentacion(textos, dict1):
    #Cambiar sustantivos
    df_aumentado = pd.DataFrame(columns=textos.columns)
    rows_to_add = []
    posTagsToAugment = [
    'adj.', 'cuant.', 'num.', 'dem.', 'det.', 'ide.', 'int.', 'interj.',  'n.', 'ono.', 'pos.',  'v.',
    ]
    #Se están mutando adjetivos, cuantificadores, números, demostrativos, determinantes, ideófonos, interrogativos, interjecciones, sustantivos, onomatopeyas, posposiciones y verbos

    for index, row in textos.iterrows():
        cambiarMorfemas(row, posTagsToAugment, rows_to_add, dict1)
        alterarPronombres(row, rows_to_add, dict1)
        insertarRuido(row, rows_to_add, dict1)

        
    df_aumentado = pd.concat([df_aumentado, pd.DataFrame(rows_to_add)], ignore_index=True)
    print(df_aumentado.shape)
    return df_aumentado



def etapa_vectorizacion(tokens, embeddings=None):
    if embeddings is None:
        #Descargar embeddings
        return
    #Se necesita un modelo de embeddings para poder vectorizar los tokens
    
    return



def pipeline(df):
    dict1 =estructurasAuxiliares(df)
    tokenizador = descargarTokenizador()
    df_aumentado=etapa_aumentacion(df, dict1)
    df = pd.concat([df, df_aumentado], ignore_index=True)
    df['transcription']=etapa_preprocesamiento(df['transcription'])
    df['tokens']=etapa_preprocesamiento(df['transcription'], tokenizador)
    # etapa_vectorizacion(df['transcription'])
    return df

def descargarTokenizador(language='Iskonawa'):
    import requests

    # URLs of the tokenizer files
    model_url = "https://github.com/Xnehil/Tesis/raw/main/O2_Pipeline/tokenizador" + language + ".model"
    vocab_url = "https://github.com/Xnehil/Tesis/raw/main/O2_Pipeline/tokenizador" + language + ".vocab"

    # Download the model file
    model_response = requests.get(model_url)
    with open('tokenizador' + language + '.model', 'wb') as model_file:
        model_file.write(model_response.content)

    # Download the vocab file
    vocab_response = requests.get(vocab_url)
    with open('tokenizador' + language + '.vocab', 'wb') as vocab_file:
        vocab_file.write(vocab_response.content)

    sp = spm.SentencePieceProcessor()
    sp.load('tokenizador' + language + '.model')
    return sp

def alterarPronombres(row, rowsToAdd, dict1, prob=0.3):
    keys_array = [
    '1PL', '1PL.P', '1PL:A', '1PL:NOM', '1PL:S', '1SG', '1SG.ABS(SK)', '1SG.GEN(SK)', 
    '1SG:A', '1SG:A(SK)', '1SG:ERG', '1SG:GEN', '1SG:P', '1SG:S', '1SG:S(SK)', 
    '2PL(SK)', '2PL:P(SK)', '2PL:S(SK)', '2SG', '2SG.ABS(SK)', '2SG:A', '2SG:ABS', 
    '2SG:ERG', '2SG:GEN', '2SG:P', '2SG:S', '2SGS', '3PL', '3PL(SK)', '3PL:A', 
    '3SG', '3SG(SK)', '3SG:A', '3SG:GEN'
    ]
    targetDict = {
    "1S": {"A": "ena", "S": "eah", "P": "ea"},
    "2S": {"A": "mi", "S": "mi", "P": "mia"},
    "3S": {"A": "oanton", "S": "oa", "P": "oa"},
    "1PL_Inclusivo": {"A": "non(bo)", "S": "no(bo)", "P": "no(bo)"},
    "1PL_Exclusivo": {"A": "enabo", "S": "eahbo", "P": "eabo"},
    "2PL": {"A": "mibo", "S": "mibo", "P": "miabo"},
    "3PL": {"A": "aboton", "S": "abo", "P": "abo"}
    }

    if pd.isnull(row['morpheme_break']) or pd.isnull(row['pos']) or pd.isnull(row['gloss_es']):
        return
    morphemes, pos_tags, glosses = parse_morphemes(row)
    for morpheme, pos_tag, gloss in zip(morphemes, pos_tags, glosses):
        if gloss in keys_array and random.random() < prob:
            if ':' in gloss or '.' in gloss:
                # Parse gloss
                persona, forma = re.split(r'[:.]+', gloss)
                # Remove (SK) from persona or forma
                persona = persona.replace("(SK)", "")
                if forma:
                    forma = forma.replace("(SK)", "")
                    if forma not in ['A', 'S', 'P']:
                        continue
                else:
                    continue
                # Change pronoun
                persona = random.choice(list(targetDict.keys()))
                newPronoun = targetDict[persona].get(forma, None)
                newData = (newPronoun, pos_tag, persona + ":" + forma)
                newRow = createNewRow(row, newData, morpheme)
                rowsToAdd.append(newRow)
        else:
            # Handle the case where gloss does not contain a colon or a period
            continue

def insertarRuido(row, rowsToAdd, dict1, prob=0.1):
    #En transcription, se intercambiarán dos caracteres no blancos
    transcription = row['transcription']
    if len(transcription) < 2:
        return
        
    words = transcription.split()
    new_words = []
    
    for word in words:
        if len(word) < 2:
            new_words.append(word)
            continue

        if random.random() < prob:
            indicesNoBlancos = [i for i, c in enumerate(word) if not c.isspace()]
            if len(indicesNoBlancos) < 3:
                new_words.append(word)
                continue
            
            word_list = list(word)
            # Choose a random operation: swap, insert, or delete
            operation = random.choice(['swap', 'insert', 'delete'])
            
            if operation == 'swap':
                # Ensure the two characters being swapped are side-by-side
                idx = random.choice(indicesNoBlancos[1:-1])  # Choose an index that is not the last one or the first one
                idx1, idx2 = idx, idx + 1
                word_list[idx1], word_list[idx2] = word_list[idx2], word_list[idx1]
            
            elif operation == 'insert':
                # Insert a random character at a random position
                random_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                insert_pos = random.randint(0, len(word_list))
                word_list.insert(insert_pos, random_char)
            
            elif operation == 'delete':
                # Delete a random non-whitespace character
                delete_idx = random.choice(indicesNoBlancos)
                del word_list[delete_idx]
            
            new_words.append(''.join(word_list))
        else:
            new_words.append(word)
    
    newRow = row.copy()
    newRow['transcription'] = ' '.join(new_words)
    rowsToAdd.append(newRow)

def cambiarMorfemas(row, posTagsToAugment, rowsToAdd, dict1, prob=0.5):
    if pd.isnull(row['morpheme_break']) or pd.isnull(row['pos']) or pd.isnull(row['gloss_es']):
        return
    morphemes, pos_tags, glosses = parse_morphemes(row)
    new_data = None
    for morpheme, pos_tag, gloss in zip(morphemes, pos_tags, glosses):
        if pos_tag in posTagsToAugment and random.random() < prob:
            # Cambiar sustantivo
            new_data = random.choice(dict1["pos_tags"][pos_tag])
            new_data = (new_data[0],pos_tag, new_data[1])
            newRow=createNewRow(row, new_data, morpheme)
            rowsToAdd.append(newRow)



def createNewRow(row, new_data, replacedMorpheme):
    newRow = row.copy()
    #Reemplazar en row el morfema por la clave de new_data
    newRow['morpheme_break'] = newRow['morpheme_break'].replace(replacedMorpheme, new_data[0])
    #Recuperar la posición de new_data
    position = newRow['morpheme_break'].split().index(new_data[0])
    #Reemplazar en row el pos en la posición correspondiente
    newRow['pos'] = newRow['pos'].split()
    newRow['pos'][position] = new_data[1]
    newRow['pos'] = " ".join(newRow['pos'])
    #Reemplazar en row el gloss en la posición correspondiente
    newRow['gloss_es'] = newRow['gloss_es'].split()
    newRow['gloss_es'][position] = new_data[2]
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
        #Reemplazar posibles _ por espacio en blanco
        morpheme = morpheme.replace('_', ' ')
        if morpheme.startswith("=") or morpheme.startswith("-"):
            new_morpheme = morpheme[1:]
        else:
            if text and not text.endswith(" "):
                text += " "
            new_morpheme = morpheme
        # Si el nuevo morfema comienza con la misma letra con la que el texto terminaba, solo se usa una
        if text and new_morpheme and text[-1] == new_morpheme[0]:
            if len(new_morpheme) > 1:
                text += new_morpheme[1:]
            else:
                text += new_morpheme
        else:
            text += new_morpheme
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
    pos_tags = [normalizePos(tag) for tag in row['pos'].split()]
    glosses = row['gloss_es'].split()

    return morphemes, pos_tags, glosses
    # morphemes = row['morpheme_break']
    # pos_tags = row['pos']
    # glosses = row['gloss_es']
    # arr_morphemes = []
    # arr_pos_tags = []
    # arr_glosses = []
    # curr_morpheme = ""
    # curr_pos_tag = ""
    # curr_gloss = ""
    # morphemeDone = False
    # posTagDone = False
    # glossDone = False


    # for i in range(np.min([len(morphemes), len(pos_tags), len(glosses)])):
    #     curr_morpheme += morphemes[i]
    #     curr_pos_tag += pos_tags[i]
    #     curr_gloss += glosses[i]
    #     if morphemes[i] == ' ' and pos_tags[i] == ' ' and glosses[i] == ' ':
    #         arr_morphemes.append(curr_morpheme.strip())
    #         arr_pos_tags.append(curr_pos_tag.strip())
    #         arr_glosses.append(curr_gloss.strip())
    #         curr_morpheme = ""
    #         curr_pos_tag = ""
    #         curr_gloss = ""

    # #Completar los últimos morfemas desde donde se quedaron
    # if i + 1 < len(morphemes):
    #     curr_morpheme += morphemes[i + 1:]
    # if i + 1 < len(pos_tags):
    #     curr_pos_tag += pos_tags[i + 1:]
    # if i + 1 < len(glosses):
    #     curr_gloss += glosses[i + 1:]

    # arr_morphemes.append(curr_morpheme.strip())
    # arr_pos_tags.append(curr_pos_tag.strip())
    # arr_glosses.append(curr_gloss.strip())
    
    # return arr_morphemes, arr_pos_tags, arr_glosses


def normalizePos(pos_tag):
    normalizeMap={
        'adj': 'adj.', 'adj.': 'adj.',
        'adv': 'adv.', 'advv.': 'adv.', '-adv.': '-adv.', 
        'art.': 'art.', 
        'conec': 'conec.', 'conect.': 'conec.','conj.': 'conec.',
        'cuant.': 'cuant.','num': 'num.', 
        'dem': 'dem.', 'demadv.': 'dem.',
        'det.': 'det.',
        'ide.': 'ide.','ideo': 'ide.', 
        'int.': 'int.', 'pal.int': 'int.','prom': 'int.',
        'inter.': 'interj.', 'interj.': 'interj.', 
        'muletilla.': 'muletilla.',
        'n.': 'n.', '-n.': 'n.',
        'ono': 'ono.',  #onomatopeyas
        'part.': 'part.', #partículas
        'pos': 'pos.','post': 'pos.', 'post.': 'pos.', #posposiciones
        'pre.': 'prep.', 'pref.-': 'pre.', 'prep.': 'prep.', 
        'pron': 'pron.',
        'suf.': 'suf.', 
        'v': 'v.', 'v.amb': 'v.', 'v.ambi': 'v.', 'v.int': 'v.', 'v.intr': 'v.', 'v.tr': 'v.','-v.': 'v.',
        '-': 'punct.', '.': 'punct.', '/': 'punct.', ';': 'punct.', '?': 'punct.',
        '-lig.': '-lig.',  
        '-suf': '-suf', '-suf.': '-suf.','-sufv.intr.': '-suf.', '-suj.': '-suf.',
        'FP': 'FP', '[...]': '[...]', '[canto]': '[canto]', '\\ps': '\\ps',
        'clit': 'clit.', 'clitdem': 'clit.','clitn.': 'clit.','clitpart.': 'clit.','clitv.': 'clit.'
    } 
    return normalizeMap.get(pos_tag, pos_tag)

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





