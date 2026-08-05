FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    net-tools \
    procps \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Xray
RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && \
    rm /tmp/xray.zip

# دایرکتوری‌ها
RUN mkdir -p /var/log/xray /var/log/nginx /app/data /app/configs /etc/xray /app/static /app/templates /etc/nginx

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8000 8080 12889

CMD ["/bin/bash", "/app/start.sh"]
