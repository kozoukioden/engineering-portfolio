FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY gateway_service.py /app/gateway_service.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "gateway_service.py"]
