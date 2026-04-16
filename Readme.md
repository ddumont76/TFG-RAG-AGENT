# TFG – Agente RAG para la asistencia inteligente en resolución de incidencias

Este proyecto implementa un sistema RAG (Retrieval-Augmented Generation) orientado a la asistencia técnica en la resolución de incidencias en entornos de Data e Inteligencia Artificial.

El sistema combina búsqueda semántica sobre tickets y documentación técnica, modelos de lenguaje locales mediante Ollama y una evaluación opcional de la calidad de las respuestas mediante métricas RAGAS.

El proyecto tiene un enfoque académico y demostrativo, priorizando claridad arquitectónica, reproducibilidad y facilidad de análisis.

---

## Arquitectura general

El flujo principal del sistema es el siguiente:

1. Carga de un corpus ficticio de tickets y documentos técnicos.
2. Generación de embeddings semánticos.
3. Almacenamiento de los embeddings en una base vectorial (ChromaDB).
4. Recuperación de contexto relevante para una consulta.
5. Generación de una respuesta mediante un modelo de lenguaje local.
6. Evaluación opcional de la respuesta utilizando métricas RAGAS.

La evaluación se ejecuta de forma desacoplada del flujo principal para evitar introducir latencia en la interacción con el usuario.

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

TFG-RAG-AGENT/
├── Dockerfile             # Fichero docker
├── docker-compose.yml     # Orquestador docker
├── .dockerignore          # Fichero para marcar que debe ignorar al dockerizar
├── .gitignore             # Fichero para marcar que debe ignorar Github
├── data/
│   ├── tickets/           # Tickets ficticios en formato JSON
│   ├── confluence/        # Documentación técnica ficticia
├── app/
│   ├── ingest/            # Ingesta de datos y generación de embeddings
│   ├── rag/               # Agente RAG y evaluación RAGAS
│   ├── api/               # API FastAPI y UI web
│   ├── services/          # Servicios auxiliares
├── chroma_db/             # Base vectorial local (no versionada)
├── requirements.txt       # Listado de dependencias
├── run_api.py
└── README.md
└── swagger.json
└── swagger.yaml

Nota: El directorio chroma_db/ se genera automáticamente y no se incluye en el repositorio.

---

## Ejecución del proyecto con Docker (recomendada)

La aplicación puede ejecutarse de forma completamente reproducible utilizando Docker y Docker Compose, evitando problemas de dependencias y diferencias entre sistemas operativos.

### Requisitos previos

- Docker Desktop instalado y en ejecución.
- Ollama instalado y ejecutándose en el sistema host.

### Arranque del servicio Ollama

Antes de levantar los contenedores, es necesario iniciar el servicio Ollama en el host:

ollama serve

Asegúrese de tener descargados los modelos utilizados:

ollama pull qwen2.5
ollama pull mistral

---

### Construcción y arranque de la aplicación

Desde la raíz del proyecto:

docker compose up --build

La primera ejecución puede tardar unos minutos debido a la descarga de dependencias.

---

### Acceso a la aplicación

Una vez arrancado el sistema:

- Interfaz web: http://localhost:8000/
- Dokumentación Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Ejecución del proyecto sin Docker (local)

Como alternativa, el proyecto también puede ejecutarse directamente en el entorno local.


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

Este proceso carga los datos y persiste la base vectorial local en ChromaDB.

---

### 4. Configuración del modelo de lenguaje (Ollama)

El sistema utiliza **Ollama** para ejecutar modelos de lenguaje de forma local, evitando el uso de servicios externos.### Instalación de OllamaOllama debe instalarse previamente desde su página oficial:https://ollama.com/Una vez instalado, verificar la instalación ejecutando:

ollama --version

---

### Arranque del servicio Ollama

Antes de ejecutar la aplicación, es necesario iniciar el servidor local de Ollama:

ollama serve

Este proceso debe mantenerse activo mientras se utiliza el sistema RAG.

---

### Descarga de los modelos utilizados

El proyecto ha sido probado con los siguientes modelos:

ollama pull qwen2.5
ollama pull mistral

Puede comprobarse que los modelos están disponibles con:

ollama list

---

### Selección del modelo

El modelo de lenguaje se selecciona dinámicamente desde la interfaz web o mediante el parámetro correspondiente en la API.

Durante el desarrollo y la evaluación se han utilizado principalmente modelos **ligeros**, adecuados para ejecución local y demostraciones académicas.


### 5. Ejecutar la aplicación

python run_api.py

La aplicación estará disponible en:

- Interfaz web: http://localhost:8000/
- Documentación Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Endpoints principales

### POST /query

Realiza una consulta RAG completa:

- Recupera tickets y documentos relevantes.
- Genera una respuesta usando un modelo de lenguaje local.

Ejemplo de entrada:

{
  "query": "Error 403 en Jenkins",
  "top_k": 5
}

---

### POST /evaluate (opcional)

Evalúa la calidad de una respuesta utilizando métricas RAGAS.

Este endpoint está pensado únicamente para análisis y demostración, no para uso interactivo por defecto.

Métricas calculadas:
- Faithfulness
- Answer Relevancy

---

## Documentación de la API (Swagger)

El proyecto expone documentación interactiva de la API mediante **Swagger**, lo que permite explorar y probar los endpoints directamente desde el navegador.

Una vez ejecutada la aplicación, la documentación está disponible en:

- **Swagger UI**: http://localhost:8000/docs  
- **Especificación OpenAPI (JSON)**: http://localhost:8000/openapi.json

Swagger se utiliza como herramienta de apoyo para la validación y demostración del funcionamiento de la API durante el desarrollo y la evaluación académica.


## Dataset artificial

El sistema utiliza un conjunto de **datos artificiales** (tickets y documentos técnicos) generados con fines académicos.

Estos datos:
- no contienen información real ni sensible,
- simulan incidencias y documentación habitual en entornos de Data e Inteligencia Artificial,
- se utilizan exclusivamente para demostrar el funcionamiento del sistema RAG.

En el repositorio se incluyen únicamente **ejemplos representativos**, mientras que el conjunto completo puede generarse automáticamente mediante los scripts de ingesta.


## Interpretación de las métricas RAGAS

Las métricas se calculan en un escenario sin respuestas de referencia (ground truth) y utilizando modelos de lenguaje ligeros.

En este contexto:
- Valores bajos de métricas son esperables.
- Se penaliza la inferencia implícita frente al uso literal del contexto.
- Métricas bajas no indican un fallo del sistema.

El sistema prioriza respuestas útiles y prácticas frente a respuestas estrictamente extractivas.

---

## Troubleshooting (resolución de problemas comunes)

### La aplicación no responde al realizar consultas

- Verifique que el servicio Ollama está en ejecución:
  ollama serve
- Asegúrese de que los modelos necesarios están descargados:
  ollama list

---

### Error de conexión con Ollama desde Docker

- Confirme que Ollama se está ejecutando en el host y escucha en el puerto 11434.
- En sistemas Windows o macOS, asegúrese de que Docker puede acceder a host.docker.internal.

---

### No se recuperan documentos o tickets

- Compruebe que el proceso de generación de embeddings se ha ejecutado correctamente:
  python -m app.ingest.create_embeddings
- Verifique que el directorio chroma_db/ contiene datos persistidos.

---

### Las métricas RAGAS devuelven valores bajos

- Este comportamiento es esperado cuando se utilizan modelos de lenguaje pequeños y evaluación sin ground truth.
- Valores bajos no implican un fallo del sistema, sino un estilo de generación inferencial.

---

### La interfaz web no se muestra

- Verifique que el contenedor o la aplicación local está exponiendo el puerto 8000.
- Acceda a http://localhost:8000/ directamente desde el navegador.

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
