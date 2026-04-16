# TFG – Agente RAG para la asistencia inteligente en la resolución de incidencias

Este proyecto implementa un sistema RAG (Retrieval‑Augmented Generation) orientado a la asistencia técnica en la resolución de incidencias en entornos de Data e Inteligencia Artificial.

El sistema combina búsqueda semántica sobre tickets y documentación técnica, modelos de lenguaje locales mediante Ollama y una evaluación opcional de la calidad de las respuestas utilizando métricas RAGAS.

El proyecto tiene un enfoque académico y demostrativo, priorizando la claridad arquitectónica, la reproducibilidad y la facilidad de análisis.

---

## Arquitectura general

El flujo principal del sistema es el siguiente:

1. Carga de un corpus ficticio de tickets y documentos técnicos.
2. Generación de embeddings semánticos.
3. Almacenamiento de los embeddings en una base vectorial (ChromaDB).
4. Recuperación de contexto relevante para una consulta.
5. Generación de una respuesta mediante un modelo de lenguaje local.
6. Evaluación opcional de la respuesta utilizando métricas RAGAS.

La evaluación se ejecuta de forma desacoplada del flujo principal para evitar introducir latencia innecesaria durante la interacción con el usuario.

---

## Interfaz de usuario (UI web)

El sistema cuenta con una **interfaz web accesible desde el navegador**, pensada para facilitar la interacción con el agente RAG sin necesidad de utilizar herramientas externas.

Desde la interfaz es posible:
- Introducir consultas en lenguaje natural.
- Seleccionar el modelo de lenguaje a utilizar.
- Visualizar la respuesta generada por el agente.
- Consultar los tickets y documentos utilizados como contexto.
- Ejecutar opcionalmente la evaluación RAGAS de la respuesta.

La interfaz se sirve directamente desde la API FastAPI y está orientada a la demostración funcional y a la validación del sistema en entornos académicos.

---

## Estructura del proyecto

TFG‑RAG‑AGENT/
├── data/
│   ├── tickets/           # Tickets ficticios en formato JSON
│   ├── confluence/        # Documentación técnica ficticia
├── app/
│   ├── ingest/            # Ingesta de datos y generación de embeddings
│   ├── rag/               # Agente RAG y evaluación RAGAS
│   ├── api/               # API FastAPI y UI web
│   ├── services/          # Servicios auxiliares
├── chroma_db/             # Base vectorial local (no versionada)
├── requirements.txt
├── run_api.py
└── README.md

Nota: el directorio chroma_db/ se genera automáticamente y no se incluye en el repositorio.

---

## Ejecución del proyecto (entorno local)

### 1. Crear entorno virtual

python -m venv venv

Activar el entorno:

Linux / WSL:
source venv/bin/activate

Windows:
venv\Scripts\activate

---

### 2. Instalar dependencias

pip install -r requirements.txt

---

### 3. Generar embeddings (una sola vez)

python -m app.ingest.create_embeddings

Este proceso carga los datos del corpus y persiste la base vectorial local en ChromaDB.

---

## Configuración del modelo de lenguaje (Ollama)

El sistema utiliza **Ollama** para ejecutar modelos de lenguaje de forma local, evitando el uso de servicios externos.

### Instalación de Ollama

Ollama debe instalarse previamente desde su sitio oficial:

https://ollama.com/

Comprobación de la instalación:

ollama --version

---

### Arranque del servicio Ollama

Antes de ejecutar la aplicación es necesario iniciar el servicio local:

ollama serve

Este proceso debe permanecer activo mientras se utiliza el sistema RAG.

---

### Descarga de los modelos utilizados

El proyecto ha sido probado principalmente con los siguientes modelos:

ollama pull qwen2.5
ollama pull mistral

Los modelos disponibles pueden consultarse con:

ollama list

---

### Selección del modelo

El modelo de lenguaje se selecciona dinámicamente desde la interfaz web o mediante los parámetros de la API. Durante el desarrollo se han priorizado modelos ligeros, adecuados para ejecución local y evaluación académica.

---

## Ejecutar la aplicación

python run_api.py

La aplicación estará disponible en:

- Interfaz web: http://localhost:8000/
- Documentación Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Endpoints principales

### POST /query

Realiza una consulta RAG completa:
- recupera tickets y documentos relevantes,
- genera una respuesta utilizando un modelo de lenguaje local.

Ejemplo de entrada:

{
  "query": "Error 403 en Jenkins",
  "top_k": 5
}

---

### POST /evaluate (opcional)

Evalúa la calidad de una respuesta utilizando métricas RAGAS. Este endpoint está pensado únicamente para análisis y demostración, no para uso interactivo por defecto.

Métricas calculadas:
- Faithfulness
- Answer Relevancy

---

## Dataset artificial

El sistema utiliza un conjunto de datos **artificiales** (tickets y documentos técnicos) generados con fines académicos.

Estos datos no contienen información real ni sensible y se emplean exclusivamente para demostrar el funcionamiento del sistema RAG. En el repositorio se incluyen únicamente ejemplos representativos, mientras que el conjunto completo puede generarse automáticamente mediante los scripts de ingesta.

---

## Interpretación de las métricas RAGAS

Las métricas se calculan en un escenario sin respuestas de referencia (ground truth) y utilizando modelos de lenguaje ligeros. En este contexto, valores bajos de métricas son esperables y no indican un fallo del sistema, sino un estilo de generación inferencial frente a uno extractivo.

---

## Tecnologías utilizadas

- Python 3.10+
- FastAPI
- ChromaDB
- sentence-transformers
- Ollama (LLM local)
- RAGAS (evaluación)

---

## Notas finales

- La base vectorial local no se versiona.
- El sistema está orientado a entornos académicos y demostrativos.
- La evaluación es un proceso opcional y desacoplado.
