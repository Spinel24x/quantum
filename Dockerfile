FROM python:3.11-slim

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# دانلود Xray
RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && \
    rm /tmp/xray.zip

# ساخت تمام دایرکتوری‌های مورد نیاز
RUN mkdir -p /var/log/xray \
    /var/log/nginx \
    /var/log/panel \
    /var/log/supervisor \
    /app/data \
    /app/configs \
    /etc/xray

# تنظیم پایتون
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی فایل‌ها
COPY . .

# پورت‌ها
EXPOSE 8000 12889 8443

# استارت با Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
