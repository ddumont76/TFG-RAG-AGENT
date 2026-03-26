FROM python:3.10-slim

WORKDIR /app

# Evitar buffering y acelerar logs
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de tu proyecto
COPY . .

EXPOSE 8000

# Comando para arrancar FastAPI
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
