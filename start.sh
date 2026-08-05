#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

# ساخت دایرکتوری‌ها
mkdir -p /app/data /app/configs /etc/xray /var/log/xray /var/log/panel

# تولید UUID
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
    echo "✅ Default UUID generated"
fi

# ساخت کانفیگ Xray
UUID=$(cat /app/data/uuid.txt)
cat > /etc/xray/config.json << EOF
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
                "id": "$UUID",
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

echo "✅ Xray config created"

# استارت Xray در بکگراند
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started (PID: $!)"

# استارت پنل (همه فایل‌ها توی /app هستن)
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
