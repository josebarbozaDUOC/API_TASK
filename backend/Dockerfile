# backend/Dockerfile
# agregar si o si el 'COPY .env.example .' para que pueda ser leido por el backend/app/config/settings.py

FROM python:3.13-slim
WORKDIR /app
# Instalar curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt .
COPY .env.example .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8000

# Healthcheck dinámico usando variables de entorno
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]