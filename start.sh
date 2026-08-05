#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

# اطمینان از وجود دایرکتوری‌ها (اینبار توی runtime)
mkdir -p /app/data /app/configs /etc/xray /var/log/xray /var/log/nginx /var/log/panel

# تولید UUID پیش‌فرض اگر وجود نداشته باشه
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
    echo "✅ Default UUID generated"
fi

# کپی کانفیگ اولیه Xray اگر وجود نداشته باشه
if [ ! -f /etc/xray/config.json ]; then
    echo "Creating initial Xray config..."
    cat > /etc/xray/config.json << 'EOF'
{
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [{
        "port": 12889,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {
            "clients": [{
                "id": "00000000-0000-0000-0000-000000000000",
                "level": 0
            }],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {
                "path": "/ws"
            }
        }
    }],
    "outbounds": [{
        "protocol": "freedom",
        "tag": "direct"
    }]
}
EOF
    echo "✅ Initial Xray config created"
fi

# استارت سرویس‌ها با Supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
