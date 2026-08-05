FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && \
    rm /tmp/xray.zip

RUN mkdir -p /var/log/xray /app/data /app/configs /etc/xray /app/static /app/templates

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8000 8080

CMD ["/bin/bash", "/app/start.sh"]
