# Empezamos #
1. Iniciar si no está dockerizado
2. Clone del repositorio: git clone
3. Abrimos nueva terminal sobre el proyecto y creamos el entorno de desarrollo
  cd C:\Users\dedug\Documents\Master_IA\work\TFG-RAG-AGENT>
  python -m venv venv ( Python -- version 3.14.2)
4. Activamos el entorno:
  .\venv\Scripts\activate 
# Instalamos todas las dependencias del proyecto 
  pip install -r requirements.txt
# Ejecutar run_api.py
python run_api.py
###################################
## PASO 1 ESTRUCTURA DE CARPETAS ##
###################################

tfg-rag-agent/
│── data/
│   ├── tickets/
│   ├── confluence/
│── app/
│   ├── ingest/
│   ├── rag/
│   ├── api/    ✅ FastAPI implementada
│── venv/       (se generará automáticamente)
│── requirements.txt
│── run_api.py  ✅ Script para ejecutar la API

data/tickets/ → JSON de tus tickets ficticios.
data/confluence/ → JSON o Markdown con la documentación.
app/ingest/ → scripts para cargar datos y generar embeddings.
app/rag/ → pipeline de búsqueda y recuperación.
app/api/ → FastAPI con endpoints REST.

##################################
## PASO 2 Crear entorno virtual ##
##################################
WINDOWS:

python -m venv venv
venv\Scripts\activate

Success: virtual environment created and activated, and Python/pip are on the venv path.

Python 3.14.3
pip 25.3

#################################################
## PASO 3 instala requirements.txt ##
##################################################
pip install --upgrade pip (actualizar las herramientas a las ultimas versiones)
pip install -r requirements.txt

\venv\Scripts\activate; pip install -r requirements.txt

Success: pip upgraded to 26.0.1 in your venv.
You’re now fully set up and ready to run the project’s Python scripts.

Hubo problemas al ejecutar el create_embeddings.py porque no estaba instalado requeriments.txt correctamente:
python -m venv venv
activate
pip install -r requirements.txt
pip install chromadb
pip install sentence-transformers
Verificación:

###############################
## PASO 4 Ejecutar la API ##
###############################

Para ejecutar la API FastAPI:

venv\Scripts\python.exe run_api.py

O directamente:
venv\Scripts\python.exe -m app.api.main

La API estará disponible en:
- http://localhost:8000/docs (Documentación interactiva Swagger)
- http://localhost:8000/health (Health check)
- http://localhost:8000/openapi.json (Especificación OpenAPI JSON)
- swagger.json (Archivo estático generado)
- swagger.yaml (Archivo estático generado)

## Endpoints disponibles:

### GET /health
Verifica el estado del sistema y cuenta de documentos indexados.

### POST /query
Realiza una consulta RAG completa (tickets + docs + respuesta generada).

**Request Body:**
```json
{
  "query": "problemas con S3",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "problemas con S3",
  "answer": "**Análisis del problema**: Se encontraron varios tickets relacionados con errores de permisos en S3...\n\n**Tickets relacionados encontrados**:\n1. **Ticket ID: TCK-001** - Summary: Data lake ingestion falla en S3 con errores de permisos\n2. **Ticket ID: TCK-007** - Summary: Jobs de Glue no pueden escribir en bucket S3\n\n**Posibles soluciones de documentos**:\n1. **Documento ID: DOC-005** - Title: Guía de resolución de errores de acceso S3\n   Content: Se describe: roles IAM, políticas de bucket, configuración de Glue...\n\n**Recomendación final**: Revisar roles IAM y políticas de bucket S3...",
  "tickets": [
    {
      "id": "TCK-001",
      "summary": "Data lake ingestion falla en S3 con errores de permisos",
      "description": "Los jobs de Glue no pueden escribir...",
      "comments": ["Se sospecha cambio de RW"],
      "content": "Data lake ingestion falla en S3...",
      "score": 0.85
    }
  ],
  "docs": [
    {
      "id": "DOC-005", 
      "title": "Guía de resolución de errores de acceso S3 en pipelines Glue",
      "content": "Se describe: roles IAM, políticas...",
      "score": 0.78
    }
  ],
  "model_name": "mistral",
  "processing_time": 2.34,
  "total_sources": 6,
  "confidence_score": 0.87,
  "metadata": {...}
}
```

### GET /ask?query=...&top_k=5
Endpoint alternativo para consultas RAG via GET (útil para navegadores).

**Ejemplo:** `GET /ask?query=problemas%20con%20S3&top_k=3`

### GET /search/tickets?query=...&top_k=5
Buscar únicamente en tickets.

**Response:**
```json
{
  "query": "problemas con S3",
  "tickets": [
    {
      "id": "TCK-001",
      "summary": "Data lake ingestion falla en S3 con errores de permisos",
      "description": "Los jobs de Glue no pueden escribir en el bucket...",
      "comments": ["Se sospecha cambio de RW en el bucket"],
      "content": "Data lake ingestion falla en S3...",
      "score": 0.85
    }
  ],
  "count": 1
}
```

### GET /search/docs?query=...&top_k=5
Buscar únicamente en documentos de Confluence.

**Response:**
```json
{
  "query": "problemas con S3", 
  "docs": [
    {
      "id": "DOC-005",
      "title": "Guía de resolución de errores de acceso S3 en pipelines Glue",
      "content": "Se describe: roles IAM, políticas de bucket...",
      "score": 0.78
    }
  ],
  "count": 1
}
```

### POST /evaluate
Evalúa la calidad de una respuesta RAG usando métricas RAGAS.

**Métricas calculadas:**
- **Faithfulness**: Fidelidad de la respuesta a los documentos recuperados (0-1)
- **Answer Relevancy**: Relevancia de la respuesta a la consulta original (0-1)
- **Context Precision**: Precisión de documentos recuperados (0-1)
- **Context Recall**: Recall de documentos relevantes (0-1)

**Request Body:**
```json
{
  "query": "¿Cómo resolver errores 403 en Jenkins?",
  "answer": "Los errores 403 en Jenkins ocurren cuando hay problemas de credenciales...",
  "contexts": ["Documento 1 relevante", "Documento 2 relevante"],
  "ground_truth": "Respuesta esperada (opcional)"
}
```

**Response:**
```json
{
  "query": "¿Cómo resolver errores 403 en Jenkins?",
  "answer": "Los errores 403 en Jenkins ocurren...",
  "metrics": {
    "faithfulness": 0.85,
    "answer_relevancy": 0.92,
    "context_precision": 0.88,
    "context_recall": 0.80
  },
  "avg_score": 0.8625,
  "metric_descriptions": {...}
}
```


#################################################
## PASO 4 Crear tu corpus ficticio ##
##################################################
4.1 Tickets ficticios en JSON
Crea archivos dentro de data/tickets/:
data/tickets/ticket_001.json


{
    "id": "TCK-001",
    "summary": "Error en pipeline de Jenkins",
    "description": "El job falla al intentar descargar dependencias Maven. Error: 403 forbidden.",
    "comments": [
        "Puede ser problema de credenciales.",
        "Revisar configuración en settings.xml."
    ]
}

 4.2 Documentos de Confluence ficticios
Crea archivos dentro de data/confluence/:
data/confluence/doc_jenkins.json

{
  "id": "DOC-001",
  "title": "Guía de resolución de errores en Jenkins",
  "content": "Para errores 403 en Jenkins revisa las credenciales... También asegúrate de que el settings.xml tiene el servidor configurado correctamente."
}

################################################################
## PASO 5 Crear el script de Ingesta (sin embeddings todavía) ##
################################################################
C:\Users\deborah.dumontgonzal\work\tfg-rag-agent> python app/ingest/load_corpus.py

Archivos encontrados: ['doc_jenkins.json', 'doc_k8s.json']
Total JSON cargados: 2

TICKETS CARGADOS:
- JIR-001: Error en pipeline de Jenkins
- JIR-002: Problema al desplegar en Kubernetes

DOCUMENTOS DE CONFLUENCE CARGADOS:
- DOC-001: Guía de resolución de errores en Jenkins
- DOC-002: Solución a errores CrashLoopBackOff


################################################################
## PASO 6 Crear embeddungs e indexar datos en ChromaDB ##
################################################################

app/ingest/create_embeddings.py

Este script hará:

Cargar tickets y documentos (usando las funciones que ya tenemos).
Crear embeddings con sentence-transformers.
Crear colecciones en ChromaDB:

tickets_collection
docs_collection


Insertar los documentos + metadatos.
Probar una consulta semántica.

## Instalar el modelo de embeddings

pip install sentence-transformers


## Ejecutar la ingesta en ChromaDB
python app/ingest/create_embeddings.py

🔄 Cargando modelo de embeddings...
📨 Encontrados 2 tickets
✅ Tickets almacenados en ChromaDB
📄 Encontrados 2 documentos
✅ Documentos almacenados en ChromaDB

🔎 Buscando similitud para: El pipeline de Jenkins devuelve un error 403

🎟️ Tickets similares:
- Error en pipeline de Jenkins...
📚 Documentos similares:
- Guía de resolución de errores en Jenkins...

Significaría que el primer motor de RAG ya funciona:
Ya tienes:

Corpus en JSON
Carga de datos
Embeddings
Base vectorial ChromaDB persistida
Búsqueda semántica en tickets y docs

## Creamos un check para ver la carga de embeddings en chromadb
venv\Scripts\python.exe app/ingest/check_corpus_simple.py

## Creamos un script de carga e indexamos
load_corpus.py

## Integrar con create_embeddings.py para refrescar index automáticamente tras la generación.


La integración está completa y funcionando correctamente. Ahora, al ejecutar generate_corpus.py, automáticamente:

Genera el corpus con 30 tickets y 30 documentos de Data & IA
Refresca los embeddings en ChromaDB sin necesidad de ejecutar create_embeddings.py manualmente
El índice se mantiene actualizado automáticamente tras cada generación de datos. La verificación confirma que todo funciona: 32 tickets y 30 documentos indexados, con búsqueda semántica operativa.

Nota opcional: Hay una advertencia de deprecación en datetime.utcnow(), pero no afecta la funcionalidad. Si quieres actualizarlo, podemos cambiarlo a datetime.now(datetime.timezone.utc) en futuras iteraciones.

Tu pipeline de ingestión ahora es completamente automatizado: genera datos → indexa embeddings → listo para RAG. 🚀


################################################################
## PASO 7 Crear el módulo RAG del agente ##
################################################################
Incluye:

Función de búsqueda unificada tickets + docs
Ranking combinado
Preparación del contexto para un LLM
Respuestas con referencias

################################################################
## PASO 8 Crear API con Instalar FastAPI + Uvicorn ##
################################################################


Archivos creados:
main.py - API FastAPI principal con endpoints /query y /health
__init__.py - Paquete Python
run_api.py - Script conveniente para ejecutar la API
Actualizado requirements.txt con fastapi y uvicorn[standard]
🔗 Endpoints disponibles:
GET /health

Verifica estado del sistema
Retorna conteo de tickets y documentos indexados
POST /query

Recibe consultas en español sobre temas de Data & IA
Retorna documentos relevantes (tickets + docs) + respuesta generada
Soporta parámetro top_k para controlar resultados
🚀 Cómo ejecutar:
Accede a:

Documentación interactiva: http://localhost:8000/docs
Health check: http://localhost:8000/health
✅ Funcionalidades probadas:
✅ Carga automática de modelo de embeddings
✅ Conexión a ChromaDB con datos indexados (32 tickets, 30 docs)
✅ Búsqueda semántica funcional
✅ Generación de respuestas basada en documentos recuperados
✅ Manejo de errores y validación de requests

Instalamos fastAPI
DEntro de api/main.py
Con endpoints como:

/ask?query=...
/health
/search/tickets
/search/docs


################################################################
## PASO 9 Documentación Swagger/OpenAPI ##
################################################################

Archivos generados:
- swagger.json - Especificación OpenAPI/Swagger en formato JSON
- swagger.yaml - Especificación OpenAPI/Swagger en formato YAML (más legible)
- generate_swagger.py - Script para regenerar la documentación

Para regenerar la documentación después de cambios en la API:
```bash
venv\Scripts\python.exe generate_swagger.py
```

Estos archivos contienen la documentación completa de la API y pueden ser utilizados para:
- Importar en herramientas como Postman
- Generar clientes SDK automáticamente
- Documentación offline
- Integración con gateways API


################################################################
## PASO 9.5 Evaluación RAGAS - Métricas de Calidad ##
################################################################

Instalamos RAGAS para evaluar la calidad del sistema RAG:

```bash
pip install ragas
```

Archivos creados:
- app/rag/evaluation.py - Módulo de evaluación RAGAS
- evaluate_rag.py - Script para evaluación batch

**Métricas disponibles:**

1. **Faithfulness**: ¿Qué tan fiel es la respuesta a los documentos? (0-1)
2. **Answer Relevancy**: ¿Qué tan relevante es la respuesta a la consulta? (0-1)
3. **Context Precision**: ¿Qué proporción de documentos son relevantes? (0-1)
4. **Context Recall**: ¿Qué proporción de documentos relevantes fueron recuperados? (0-1)

**Uso via API:**

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo resolver errores 403 en Jenkins?",
    "answer": "Los errores 403 ocurren por problemas de credenciales...",
    "contexts": ["Documento 1", "Documento 2"],
    "ground_truth": "Respuesta esperada (opcional)"
  }'
```

**Evaluación batch (script):**

```bash
venv\Scripts\python.exe evaluate_rag.py
```

Genera reporte en `evaluation_report.json` con:
- Puntuaciones de cada métrica
- Score promedio del sistema
- Detalles de consultas evaluadas

**Interpretación de resultados:**
- Score >= 0.8: Excelente calidad
- Score 0.6-0.8: Buena calidad (puede mejorar)
- Score < 0.6: Baja calidad (requiere mejoras)


################################################################
## PASO 10 Crear agente RAG ##
################################################################
//Instalamos el servidor ollama desde Porwersehell:
irm https://ollama.com/install.ps1 | iex

ollama --version
ollama version is 0.18.3
#arrancar servidor
ollama serve

ollama pull mistral
ollama list
    mistral:latest    6577803aa9a0    4.4 GB    6 seconds ago
# Probamos que funciona por consola: 
PS C:\Users\deborah.dumontgonzal> ollama run mistral "Hola, ¿estás funcionando?"
 Claro que sí, está funcionando perfectamente. ¿Cómo puedo ayudarte hoy?



################################################################
## PASO 10 Dockerizar la aplicación ##
################################################################

Instalamos extension de docker en vsCode e instalamos versión de Docker Desktop de windows desde la store.
Se crean los 3 archivos:
1. Dockerfile
    instala tu app
    expone la API
    arranca FastAPI dentro del contenedor
2. docker-compose.yml
    Crea la imagen
    La ejecuta
    Expone FastAPI en localhost:8000
    Permite que ChromaDB persista en tu máquina
    Permite que Ollama funcione desde el host
3. .dockerignore

Vamos a generar un proyecto Docker que contenga:

Tu API FastAPI (con interfaz HTML incluida)
Tu almacenamiento persistente de ChromaDB
Conexión automática con Ollama (opcional)
Todo empaquetado en una sola imagen portátil
Listo para enviarlo a otro equipo

El examen final (tu evaluador) solo necesitará:
docker compose up

Y abrir:
http://localhost:8000/