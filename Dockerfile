FROM python:3.11-slim

WORKDIR /app

# system deps for some python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

# create dirs used by app
RUN mkdir -p /app/artifacts /app/logs

# default: run API (docker-compose overrides for streamlit)
CMD ["uvicorn", "src.app_api:app", "--host", "0.0.0.0", "--port", "8000"]