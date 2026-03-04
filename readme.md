# Resumen de Tesis

## Diseño e implementación de una herramienta para la generación de texto en la lengua Iskonawa

**Autor:** Harvy Martínez

[Ver extracto completo de la tesis](https://github.com/Xnehil/Tesis/blob/main/ExtractoTesisGeneralidades.pdf)

---

## Problema central

Existe incertidumbre sobre la efectividad de las técnicas de PLN basadas en aprendizaje profundo para generar datos útiles en una lengua con pocos recursos como el Iskonawa.

## Objetivo general

Adaptar y desarrollar modelos de generación de texto en Iskonawa mediante métodos de PLN para evaluar su efectividad en el incremento de la cantidad de datos en esta lengua.

---

## Objetivos y resultados

### O1. Diseñar y desarrollar un corpus monolingüe de la lengua Iskonawa

Se estructuró un corpus con **3942 registros** (entre frases y oraciones) provenientes de grabaciones previas. La mayor parte del contenido son transcripciones de narraciones orales iskonawa. Se organizó en atributos que incluyen segmentación morfológica, etiquetado POS, glosas en español y traducciones libres. El corpus fue publicado en formato JSON en un repositorio público.

[Ver detalle del objetivo 1 →](https://github.com/Xnehil/Tesis/blob/main/O1_Corpus/ExtractoTesisObjetivo1.pdf)

---

### O2. Aplicar técnicas de preprocesamiento, aumentación y vectorización

**Preprocesamiento:** Limpieza de caracteres especiales, normalización de mayúsculas y tokenización mediante Byte-Pair Encoding (BPE).

**Aumentación:** Se duplicó la cantidad de registros (de 3942 a **7792**) mediante:
- Inserción de ruido aleatorio
- Variación de pronombres
- Mutación controlada de morfemas basada en la [gramática Iskonawa](https://repositorio.pucp.edu.pe/index/handle/123456789/163982) (Zariquiey, 2015)

**Vectorización:** Se evaluaron 4 técnicas:
- [Anchored bi- and multilingual word embeddings](https://aclanthology.org/2021.acl-short.30/) (Eder et al., 2021)
- [Contextualised cross-lingual word embeddings](https://aclanthology.org/2021.mrl-1.2/) (Wada et al., 2020)
- Mezcla de los dos anteriores
- FastText

El primer método resultó el más adecuado según métricas de clusterización (silhouette score, índice de Davies-Bouldin e índice de Calinski-Harabasz).

[Ver detalle del objetivo 2 →](https://github.com/Xnehil/Tesis/blob/main/O2_Pipeline/ExtractoTesisObjetivo2.pdf)

---

### O3. Definición y desarrollo de los modelos generativos

Se adaptaron y entrenaron 4 arquitecturas:

| Modelo | Enfoque | Características | Artículo original |
|--------|---------|-----------------|-------------------|
| **ZmBART** | Transfer learning | Basado en mBART, entrenado con tarea auxiliar de generación parcial | [ZmBART (2021)](https://aclanthology.org/2021.findings-acl.248/) |
| **Meta-XNLG** | Transfer learning + meta-learning | Basado en mT5, pre-entrenado en 30 lenguas | [Meta-XNLG (2022)](https://aclanthology.org/2022.findings-acl.24/) |
| **LSTM** | Desde cero | Línea base con 2 capas bidireccionales, embeddings congelados | - |
| **T5** | Desde cero | Arquitectura t5_small con span corruption e i.i.d. denoising | [Ulčar y Robnik-Šikonja (2023)](https://aclanthology.org/2023.eacl-main.139/) |

#### Evaluación automática (métricas intrínsecas)

*Si bien estas métricas dan una idea del rendimiento de los modelos, no permiten concluir respecto a la calidad del contenido.*

| Modelo | Perplejidad (↓) | Distinct-2 (↑) | Distinct-3 (↑) | MAUVE (↑) |
|--------|-----------------|----------------|----------------|-----------|
| ZmBART | 43.41 | 0.0382 | 0.1181 | 0.0316 |
| MetaXNLG | 53.82 | 0.0657 | 0.2042 | **0.5293** |
| LSTM | **2473.10** | **0.0713** | **0.2672** | 0.4121 |
| T5 | 169.55 | 0.0723 | 0.1916 | 0.0090 |

Ningún modelo destacó consistentemente en todas las métricas, y el LSTM simple (línea base) no fue superado claramente por las alternativas más complejas.

[Ver detalle del objetivo 3 →](https://github.com/Xnehil/Tesis/blob/main/O3_modelos/ExtractoTesisObjetivo3.pdf)

---

### O4. Validación del contenido generado con experto

Se desarrolló una aplicación web para facilitar la validación manual del contenido generado. El protocolo de validación con el experto en la lengua consideró tres dimensiones:

- **Fluidez** (1-5): qué tan natural es el texto
- **Correctitud** (1-5): qué tan gramaticalmente correcto es
- **Pertinencia** (sí/no): si aparenta ser Iskonawa

Se evaluaron **40 ejemplos**: 8 por cada modelo (ZmBART, MetaXNLG, LSTM), 8 de datos aumentados y 8 del corpus original (control).

| Fuente | Fluidez | Correctitud | Pertinencia |
|--------|---------|-------------|-------------|
| ZmBART | 1.75 | 1.88 | 37.5% |
| MetaXNLG | 2.75 | 3.25 | 87.5% |
| LSTM | 1.63 | 1.63 | 37.5% |
| **Datos aumentados** | **4.38** | **4.25** | **100%** |
| Datos originales | 4.63 | 4.63 | 100% |

[Ver detalle del objetivo 4 →](https://github.com/Xnehil/Tesis/blob/main/O4_Aplicacion/ExtractoTesisObjetivo4.pdf)

---

## Conclusiones

- **Ninguno de los modelos de aprendizaje profundo** (ZmBART, MetaXNLG, LSTM) logró generar contenido útil en Iskonawa según la evaluación del experto. Las puntuaciones en fluidez y correctitud fueron bajas, y solo MetaXNLG alcanzó un 87.5% en pertinencia, pero con baja calidad lingüística.

- **Los datos aumentados mediante conocimiento lingüístico** (basado en la gramática Iskonawa y anotaciones morfológicas) obtuvieron puntuaciones cercanas a los datos reales (4.38/5 en fluidez, 4.25/5 en correctitud, 100% pertinencia).

- Para lenguas con recursos extremadamente limitados como el Iskonawa, el **enfoque basado en reglas lingüísticas y aumentación controlada** resulta más efectivo que el aprendizaje profundo para generar contenido utilizable.

[Ver extracto de conclusiones →](https://github.com/Xnehil/Tesis/blob/main/ExtractoTesisConclusiones.pdf)

---

## Trabajos futuros sugeridos

1. **Profundizar en métodos basados en reglas** para aumentación, aprovechando estándares como UniMorph o Universal Dependencies, y empaquetar la solución en una herramienta distribuible. El valor de esta iniciativa estaría en aprovechar al máximo el conocimiento lingüístico que se encuentra en corpus anotados.

2. **Explorar enfoques híbridos** que combinen grandes modelos de lenguaje con lexicones bilingües (ej. [Yong et al., 2024](https://aclanthology.org/2024.emnlp-main.784/)) en lugar de entrenar o ajustar modelos directamente en la lengua de bajos recursos.
