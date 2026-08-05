#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

mkdir -p /app/data /etc/xray /var/log/xray /var/log/nginx

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

UUID=$(cat /app/data/uuid.txt)

# ============================================
# Xray با VLESS + TCP خام (بدون WebSocket)
# ============================================
cat > /etc/xray/config.json << EOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 12889,
        "listen": "127.0.0.1",
        "protocol": "vless",
        "settings": {
            "clients": [{"id": "$UUID", "level": 0}],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "tcp"
        }
    }],
    "outbounds": [{"protocol": "freedom"}]
}
EOF

echo "✅ Xray config created"

# استارت Xray
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started on 127.0.0.1:12889"

# ============================================
# کپی nginx.conf به مسیر درست
# ============================================
cp /app/nginx.conf /etc/nginx/nginx.conf

# استارت Nginx (TCP Stream Proxy)
nginx -g "daemon off;" &
echo "✅ Nginx TCP→WebSocket proxy started on 0.0.0.0:8080"

# ============================================
# استارت پنل
# ============================================
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
