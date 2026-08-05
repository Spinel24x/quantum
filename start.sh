#!/bin/bash
echo "🚀 Starting EdgeX Panel..."
mkdir -p /app/data /app/static /app/templates /etc/xray /var/log/xray

# ساخت UUID
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

UUID=$(cat /app/data/uuid.txt)

# کانفیگ Xray
cat > /etc/xray/config.json << EOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 12889,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {
            "clients": [{"id": "$UUID", "level": 0}],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {"path": "/ws"}
        }
    }],
    "outbounds": [{"protocol": "freedom"}]
}
EOF

# استارت Xray
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started"

# استارت پنل
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
