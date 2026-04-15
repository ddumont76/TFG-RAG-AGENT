# app/api/metric_ranges.py

METRIC_RANGES = {
    "faithfulness": {
        "desc": "¿Qué tan fiel es la respuesta al contexto recuperado?",
        "range": "0.0 = infiel, 1.0 = totalmente fiel",
    },
    "answer_relevancy": {
        "desc": "¿Qué tan relevante es la respuesta respecto a la pregunta?",
        "range": "0.0 = no relevante, 1.0 = muy relevante",
    },
    
}