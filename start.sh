#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

# ساخت دایرکتوری‌های ضروری
mkdir -p /app/data /app/static /app/templates /etc/xray /var/log/xray

# تولید UUID اگر وجود نداشته باشه
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
    echo "✅ Default UUID generated"
fi

# خوندن UUID
UUID=$(cat /app/data/uuid.txt)

# ساخت کانفیگ Xray
cat > /etc/xray/config.json << EOF
{
    "log": {
        "loglevel": "warning",
        "access": "/var/log/xray/access.log",
        "error": "/var/log/xray/error.log"
    },
    "inbounds": [{
        "port": 12889,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {
            "clients": [{
                "id": "$UUID",
                "level": 0,
                "email": "default@edgex.panel"
            }],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {
                "path": "/ws"
            }
        },
        "sniffing": {
            "enabled": true,
            "destOverride": ["http", "tls"]
        }
    }],
    "outbounds": [{
        "protocol": "freedom",
        "tag": "direct"
    }],
    "routing": {
        "domainStrategy": "AsIs",
        "rules": []
    }
}
EOF

echo "✅ Xray config created"

# استارت Xray در بکگراند
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started (PID: $!)"

# گرفتن پورت از Railway (پیش‌فرض 8000)
PORT=${PORT:-8000}
echo "🌐 Starting Panel on port $PORT"

# استارت پنل
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT
