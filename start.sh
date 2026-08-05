#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

mkdir -p /app/data /etc/xray /var/log/xray

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

UUID=$(cat /app/data/uuid.txt)

# ============================================
# Xray: VLESS + WebSocket روی پورت 8080
# ============================================
cat > /etc/xray/config.json << EOF
{
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [{
        "port": 8080,
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

# استارت Xray
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started on port 8080"

# استارت پنل
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
