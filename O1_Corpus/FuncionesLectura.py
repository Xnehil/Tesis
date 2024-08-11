import os
import re
import pandas as pd
from langdetect import detect

def procesarOracion(bloque):
    #Quitar espacios en blanco
    bloque = bloque.strip()
    return bloque

def leerTxt(ruta="../textos", data={}):
    primera = True
    id = locutor = transcripcion =  palabras = traduccionLibre = traduccionPalabra = morfologia = pos =""


    for filename in os.listdir(ruta):
        #Si el archivo es un .txt
        if filename.endswith('.txt'):
            #Se abre el archivo
            #Saltar el archivo 'textos/DICCIONARIOISKONAWA7.txt' porque no es un archivo de texto
            if filename == 'DICCIONARIOISKONAWA7.txt':
                continue
            with open('../textos/'+filename, encoding='utf-8') as file:
                #Se lee el archivo
                transcripcion = file.read()
                #Por cada linea en el archivo
                for line in transcripcion.split('\n'):
                    #Skip si la linea es solo espacios en blanco o saltos de linea
                    if not line.strip():
                        continue
                    tipo_match = re.search(r'^\\\S*', line)
                    if tipo_match:
                        tipo = tipo_match.group()
                        # Remove the tipo from the line to get the oracion
                        oracion = re.sub(r'^\\\S* ', '', line)
                        #Quitar espacios en blnaco
                        oracion = oracion.strip()
                        
                        # Process the oracion based on the tipo
                        if tipo == '\\ref':
                            id = oracion
                            # Append the previous data before resetting variables
                            if not primera:
                                key = f"{filename}_{id}"
                                data[key] = {
                                    'id': id, 
                                    'speaker': locutor, 
                                    'transcription': transcripcion, 
                                    'text': palabras.strip(), 
                                    'gloss_es': traduccionPalabra.strip(),
                                    'free_translation': traduccionLibre,
                                    'morpheme_break': morfologia.strip(),
                                    'pos': pos.strip(),
                                    'file': filename
                                }
                            primera = False
                            # Reset the variables
                            locutor = transcripcion = palabras = traduccionLibre = traduccionPalabra = morfologia = pos = ""
                        elif tipo == '\\ELANParticipant':
                            locutor = oracion
                        elif tipo == '\\trs':
                            transcripcion = procesarOracion(oracion)
                        elif tipo == '\\tx':
                            palabras += procesarOracion(oracion) + ' '
                        elif tipo == '\\gn':
                            traduccionPalabra += oracion + ' '
                        elif tipo == '\\ft':
                            traduccionLibre = procesarOracion(oracion) 
                        elif tipo == '\\mb':
                            morfologia += oracion + ' '
                        elif tipo == '\\ps':
                            pos += oracion + ' '
                        else:
                            continue
                primera = True
    if not primera:
        key = f"{filename}_{id}"
        data[key] = {
            'id': id, 
            'speaker': locutor,
            'transcription': transcripcion,
            'text': palabras.strip(),
            'gloss_es': traduccionPalabra.strip(),
            'free_translation': traduccionLibre,
            'morpheme_break': morfologia.strip(),
            'pos': pos.strip(),
            'file': filename
        }

def leerEaf(ruta="../textos", data={}):
    #Solo se leen los archivos que no han sido procesados como .txt
    archivos = []
    for filename in os.listdir(ruta):
        if filename.endswith('.eaf'):
            if not os.path.exists('../textos/'+filename[:-4]+'.txt'):
                archivos.append(filename)

    for filename in archivos:
        locutor = texto = palabras = traduccionLibre= traduccionPalabra = morfologia = pos = id = None
        dentro_tier = False
        with open('../textos/'+filename, encoding='utf-8') as file:
            texto = file.read()
            annotation_id = None
            #Cada archivo eaf es un xml. Nos interesa el valor de los atributos 'ANNOTATION_VALUE' de los elementos 'TIER' que tengan el atributo 'TIER_ID' igual a 'trsx@algo'
            #Por cada linea en el archivo
            for line in texto.split('\n'):
                #Skip si la linea es solo espacios en blanco o saltos de linea
                if not line.strip():
                    continue
                #Buscar fin de tier
                end_tier_match = re.search(r'</TIER>', line)
                # Search for the self-closing tier pattern
                self_closing_tier_match = re.search(r'<TIER\s+.*?/>', line)

                # Check if either pattern is found
                if end_tier_match or self_closing_tier_match:
                    dentro_tier = False
                    # If it's a self-closing tier, ignore the line
                    if self_closing_tier_match:
                        continue

                if dentro_tier:
                    if tier_id.startswith('trs@'):
                        #Cosa de transcripción original
                        alignable_annotation_match = re.search(r'<ALIGNABLE_ANNOTATION[^>]*ANNOTATION_ID="([^"]+)"', line)
                        if alignable_annotation_match:
                                annotation_id = alignable_annotation_match.group(1)
                                id = annotation_id
                        if id is not None:
                            annotation_value_match = re.search(r'<ANNOTATION_VALUE>([^<]+)</ANNOTATION_VALUE>', line)
                            if annotation_value_match:
                                transcripcion = procesarOracion(annotation_value_match.group(1))
                                key = f"{filename}_{id}"
                                data[key] = {
                                    'id': id, 
                                    'speaker': locutor, 
                                    'transcription': transcripcion, 
                                    'text': palabras, 
                                    'gloss_es': traduccionPalabra,
                                    'free_translation': traduccionLibre,
                                    'morpheme_break': morfologia,
                                    'pos': pos,
                                    'file': filename
                                }
                                annotation_id = None

                    elif tier_id.startswith('tx@'):
                        ref_annotation_match = re.search(r'<REF_ANNOTATION[^>]*ANNOTATION_ID="([^"]+)" ANNOTATION_REF="([^"]+)"', line)
                        # print("Buscando referencia a anotación en tier tx")
                        if ref_annotation_match:
                            # print ("Se encontró una referencia a una anotación con valor {} y referencia {}".format(ref_annotation_match.group(1), ref_annotation_match.group(2)))
                            annotation_id = ref_annotation_match.group(1)
                            #Buscar en data el elemento con el id igual a annotation_ref y archivo igual a filename
                            annotation_ref = ref_annotation_match.group(2)
                            key = f"{filename}_{annotation_ref}"
                            # print(key)
                        if annotation_id is not None:
                            annotation_value_match = re.search(r'<ANNOTATION_VALUE>([^<]+)</ANNOTATION_VALUE>', line)
                            if annotation_value_match:
                                palabras = annotation_value_match.group(1)
                                data[key]['text'] = palabras
                                # print(key)
                                annotation_id = None
                    elif tier_id.startswith('ft@'):
                        #Cosa de traducción
                        ref_annotation_match = re.search(r'<REF_ANNOTATION[^>]*ANNOTATION_ID="([^"]+)" ANNOTATION_REF="([^"]+)"', line)
                        if ref_annotation_match:
                            annotation_id = ref_annotation_match.group(1)
                            #Buscar en data el elemento con el id igual a annotation_ref y archivo igual a filename
                            annotation_ref = ref_annotation_match.group(2)
                            key = f"{filename}_{annotation_ref}"
                            # print(key)
                        if annotation_id is not None:
                            annotation_value_match = re.search(r'<ANNOTATION_VALUE>([^<]+)</ANNOTATION_VALUE>', line)
                            if annotation_value_match:
                                traduccion = annotation_value_match.group(1)
                                # print(key)
                                data[key]['free_translation'] = traduccion
                                annotation_id = None
                else:
                    #Buscamos primero un elemento 'TIER' que tenga el atributo 'TIER_ID' igual a 'trs@algo'
                    tier_match = re.search(r'<TIER[^>]*PARTICIPANT="([^"]+)"[^>]*TIER_ID="([^"]+)"', line)
                    if tier_match:
                        locutor = tier_match.group(1)
                        tier_id = tier_match.group(2)
                        # print("Entrando en tier {} con locutor {} en archivo {}".format(tier_id, locutor, filename))
                        dentro_tier = True

def clean_text(text):
    return re.sub(r'\(\d\)', '', text).strip()

def parse_txt(file):
    #Función de Amy Trujillo para leer el diccionario
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_entry = {}
    current_tag = None
    current_value = []

    for line in lines:
        line = line.strip()
        if line.startswith('\\lx'):
            if current_entry:
                if current_tag:
                    current_entry[current_tag] = ' '.join(current_value).strip()
                data.append(current_entry)
            current_entry = {'lex_isc': clean_text(line.strip('\\lx').strip())}
            current_tag = None
            current_value = []
        elif line.startswith('\\lc'):
            current_entry['lex_citation'] = clean_text(line.strip('\\lc').strip())
            current_tag = None
            current_value = []
        elif line.startswith('\\ps'):
            current_entry['pos'] = line.strip('\\ps').strip()
            current_tag = None
        elif line.startswith('\\gn') and 'gloss_es' not in current_entry:
            if current_tag:
                current_entry[current_tag] = ' '.join(current_value).strip()
            current_tag = 'gloss_es'
            current_value = [line.strip('\\gn').strip()]
        elif line.startswith('\\rn') and 'gloss_es' not in current_entry:
            if current_tag:
                current_entry[current_tag] = ' '.join(current_value).strip()
            current_tag = 'gloss_es'
            current_value = [line.strip('\\rn').strip()]
        elif line.startswith('\\dn') and 'def_es' not in current_entry:
            if current_tag:
                current_entry[current_tag] = ' '.join(current_value).strip()
            current_tag = 'def_es'
            current_value = [line.strip('\\dn').strip()]
        elif line.startswith('\\'):
            if current_tag:
                current_entry[current_tag] = ' '.join(current_value).strip()
            current_tag = None
        else:
            if current_tag:
                current_value.append(line)

    if current_entry:
        if current_tag:
            current_entry[current_tag] = ' '.join(current_value).strip()
        data.append(current_entry)
    
    df = pd.DataFrame(data, columns=['lex_isc', 'lex_citation', 'pos', 'gloss_es', 'def_es'])
    return df



def is_spanish(text):
    try:
        return detect(text) == 'es'
    except:
        return False
    
def limpiarCorpus(df):
    print(f"Antes de limpiar: {df.shape}")
    #Español
    df = df[df.apply(lambda row: row['speaker'] == 'Dictionary' or not is_spanish(row['transcription']), axis=1)]
    print(f"Después de eliminar español: {df.shape}")
    #Eliminar filas con texto vacío
    df = df[df['transcription'].str.strip() != '']
    print(f"Después de eliminar vacíos: {df.shape}")
    #Eliminar repetidos considerando las columnas transcription y gloss_es
    df = df.drop_duplicates(subset=['transcription', 'gloss_es'])
    print(f"Después de limpiar duplicados: {df.shape}")

    return df
    
def leerCorpus(hacerLimpieza=True):
    data = {}
    leerTxt(data=data)
    leerEaf(data=data)
    df = pd.DataFrame(data).transpose().reset_index(drop=True)
    df_diccionario = parse_txt('../textos/DICCIONARIOISKONAWA7.txt')

    #Del df_diccionario, las columnas son lex_isc 	lex_citation 	pos 	gloss_es 	def_es
    #Del df, las columnas son id 	speaker 	transcription 	text 	gloss_es 	free_translation 	morpheme_break 	pos 	file

    #Unir los dos dataframes con la siguiente lógica:
    #id será un entero que se incrementa por cada fila
    #speaker será Dictionary
    #transcription será lex_citation si no es nulo o vacío, de lo contrario será lex_isc
    #text será null
    #gloss_es será gloss_es
    #free_translation será def_es
    #morpheme_break será null
    #pos será pos
    #file será DICCIONARIOISKONAWA7.txt

    df_diccionario['id'] = range(1, len(df_diccionario)+1)
    df_diccionario['speaker'] = 'Dictionary'
    df_diccionario['transcription'] = df_diccionario['lex_citation'].fillna(df_diccionario['lex_isc'])
    df_diccionario['text'] = None
    df_diccionario['free_translation'] = df_diccionario['def_es']
    df_diccionario['morpheme_break'] = None
    df_diccionario['pos'] = df_diccionario['pos']
    df_diccionario['file'] = 'DICCIONARIOISKONAWA7.txt'

    df_diccionario = df_diccionario.drop(columns=['lex_isc', 'lex_citation', 'def_es'])
    df_diccionario = df_diccionario[['id', 'speaker', 'transcription', 'text', 'gloss_es', 'free_translation', 'morpheme_break', 'pos', 'file']]

    df_diccionario['free_translation'] = df_diccionario['free_translation'].fillna(df_diccionario['gloss_es'])

    df = pd.concat([df, df_diccionario], ignore_index=True)
    df = df.dropna(subset=['transcription'])
    df = df.reset_index(drop=True)

    #Limpiar 
    if hacerLimpieza:
        df = limpiarCorpus(df)

    #Reordenar columnas tal que el orden sea id, speaker, transcription, text, morpheme_break, pos, gloss_es, free_translation, file
    df = df[['id', 'speaker', 'transcription', 'text', 'morpheme_break', 'pos', 'gloss_es', 'free_translation', 'file']]

    #Id debe ser file sin la extensión seguido de un guión y el id
    df['id'] = df['file'].str.replace('.txt', '', regex=False) + '_' + df['id'].astype(str)

    #Cualquier campo vacío o cadena vacía debe ser null
    df = df.replace('', None)

    #Eliminar filas con None en id, speaker, transcription, free_translation, file
    df = df.dropna(subset=['id', 'speaker', 'transcription', 'free_translation', 'file'])

    #Quitar '/' de transcription, text, morpheme_break, pos, gloss_es, free_translation
    df = df.applymap(lambda x: re.sub(r'/', '', x) if pd.notnull(x) else x)
    # Normalizar pos
    df['pos'] = df['pos'].apply(lambda x: normalizePos(x) if pd.notnull(x) and x.strip() != '' else x)

    
    return df


def normalizePos(pos_tags):
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
        'suf.': 'suf.', '-suf': 'suf.', '-suf.': 'suf.', 
        'v': 'v.', 'v.amb': 'v.', 'v.ambi': 'v.', 'v.int': 'v.', 'v.intr': 'v.', 'v.tr': 'v.','-v.': 'v.',
        '-': 'punct.', '.': 'punct.', '/': 'punct.', ';': 'punct.', '?': 'punct.',
        '-lig.': '-lig.',  
        '-suf': '-suf', '-suf.': '-suf.','-sufv.intr.': '-suf.', '-suj.': '-suf.',
        'FP': 'FP', '[...]': '[...]', '[canto]': '[canto]', '\\ps': '\\ps',
        'clit': 'clit.', 'clitdem': 'clit.','clitn.': 'clit.','clitpart.': 'clit.','clitv.': 'clit.'
    } 

    def replaceMatch(match):
        word = match.group(0)
        return normalizeMap.get(word, word)
    
    normalized_pos_tags = re.sub(r'\S+', replaceMatch, pos_tags)
    return normalized_pos_tags