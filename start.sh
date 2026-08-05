#!/bin/bash
set -e

echo "🚀 Starting EdgeX Panel..."

# ساخت دایرکتوری‌ها
mkdir -p /app/data /app/configs /etc/xray

# تولید UUID پیش‌فرض اگر وجود نداشته باشه
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
    echo "✅ Default UUID generated"
fi

# تنظیم Xray
python3 /app/panel/xray_manager.py --init

# استارت Xray در بکگراند
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray started on port ${XRAY_PORT:-12889}"

# استارت پنل
cd /app/panel
python3 -m uvicorn app:app --host 0.0.0.0 --port ${PANEL_PORT:-8000}
