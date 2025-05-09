# ==================== Build Aşaması ====================
FROM python:3.10-slim AS builder

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli bağımlılıkları yükle
COPY requirements.txt .

# pip'i güncelle ve paketleri kur
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt 

# ==================== Runtime Aşaması ====================
FROM python:3.10-slim

# Runtime aşamasında gereken ortam değişkenleri
ENV REDIS_HOST="redis"
ENV REDIS_PORT=6379
ENV QUEUE=""
ENV RABBITMQ_HOST="rabbitmq"
ENV RABBITMQ_USER="guest"
ENV RABBITMQ_PASSWORD="guest"
ENV BROKER_TYPE="redis"
ENV EXCHANGE_NAME="test_exchange"
ENV SENDER_TYPE="api"
ENV SENDER_HOST=""
ENV SENDER_PORT=5672
ENV SENDER_URL="guest"
ENV SENDER_PASSWORD="guest"
ENV SENDER_HEADER=""
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages


# Çalışma dizinini ayarla
WORKDIR /app

# Build aşamasından kurulan paketleri kopyala
COPY --from=builder /install /usr/local

# Consumer script'ini kopyala
COPY app.py .
COPY log_setup.py .
COPY message_broker.py .
COPY message_dispatcher.py .
COPY circuit_breaker.py .

# Consumer script'ini çalıştır
CMD ["python", "app.py"]
