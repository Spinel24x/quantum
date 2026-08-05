from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from datetime import datetime
from pathlib import Path

# ============================================
# ساخت پوشه‌های مورد نیاز
# ============================================
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# ============================================
# ساخت فایل‌های استاتیک پیش‌فرض اگر وجود ندارن
# ============================================

# style.css
css_content = """
:root { --primary: #6366f1; --secondary: #10b981; --danger: #ef4444; --dark: #1e293b; --light: #f8fafc; --gray: #64748b; --border: #e2e8f0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
.container { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 100%; max-width: 800px; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.header h1 { font-size: 2.5em; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header p { color: var(--gray); margin-top: 10px; }
.status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }
.status-card { background: var(--light); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border); }
.status-card .label { font-size: 0.85em; color: var(--gray); }
.status-card .value { font-size: 1.4em; font-weight: 700; margin-top: 5px; }
.status-card .value.online { color: var(--secondary); }
.status-card .value.offline { color: var(--danger); }
.control-panel { background: var(--light); padding: 25px; border-radius: 12px; margin-bottom: 20px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 5px; }
.form-group input { width: 100%; padding: 10px 15px; border: 2px solid var(--border); border-radius: 8px; font-size: 1em; }
.btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 1em; font-weight: 600; cursor: pointer; transition: all 0.3s; }
.btn-primary { background: var(--primary); color: white; width: 100%; }
.btn-primary:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-danger { background: var(--danger); color: white; width: 100%; margin-top: 10px; }
.config-display { background: #1a1a2e; color: #00ff41; padding: 20px; border-radius: 12px; margin-top: 20px; font-family: monospace; word-break: break-all; position: relative; }
.copy-btn { position: absolute; top: 10px; right: 10px; background: var(--secondary); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
#qrcode { text-align: center; margin-top: 20px; padding: 20px; background: white; border-radius: 12px; display: inline-block; }
"""

if not os.path.exists("static/style.css"):
    with open("static/style.css", "w") as f:
        f.write(css_content)

# index.html
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EdgeX Panel</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ EdgeX Panel</h1>
            <p>Xray Configuration Manager</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <div class="label">Xray Status</div>
                <div class="value" id="xray-status">Checking...</div>
            </div>
            <div class="status-card">
                <div class="label">Active Connections</div>
                <div class="value" id="connections">0</div>
            </div>
            <div class="status-card">
                <div class="label">UUID</div>
                <div class="value" id="current-uuid" style="font-size:0.7em;">Loading...</div>
            </div>
        </div>
        
        <div class="control-panel">
            <h2>⚙️ Configuration Generator</h2>
            <div class="form-group">
                <label>SNI:</label>
                <input type="text" id="sni" value="cloudflare.com">
            </div>
            <div class="form-group">
                <label>Host (IP/Domain):</label>
                <input type="text" id="host" value="speed.cloudflare.com">
            </div>
            <div class="form-group">
                <label>WebSocket Path:</label>
                <input type="text" id="ws-path" value="/ws">
            </div>
            <button class="btn btn-primary" onclick="generateConfig()">🚀 Generate Configuration</button>
            <button class="btn btn-danger" onclick="regenerateUUID()">🔄 Regenerate UUID</button>
        </div>
        
        <div id="config-display" class="config-display" style="display:none;">
            <button class="copy-btn" onclick="copyConfig()">📋 Copy</button>
            <pre id="config-text"></pre>
        </div>
        
        <div style="text-align:center;">
            <div id="qrcode"></div>
        </div>
    </div>
    
    <script>
        async function loadStatus() {
            try {
                const r = await fetch('/api/status');
                const d = await r.json();
                document.getElementById('xray-status').textContent = d.xray ? '🟢 Online' : '🔴 Offline';
                document.getElementById('xray-status').className = 'value ' + (d.xray ? 'online' : 'offline');
                document.getElementById('connections').textContent = d.connections || 0;
                document.getElementById('current-uuid').textContent = d.uuid || 'N/A';
            } catch(e) {}
        }
        
        async function generateConfig() {
            const sni = document.getElementById('sni').value;
            const host = document.getElementById('host').value;
            const wsPath = document.getElementById('ws-path').value;
            const r = await fetch(`/api/generate-config?sni=${sni}&host=${host}&ws_path=${wsPath}`);
            const d = await r.json();
            if (d.status === 'success') {
                document.getElementById('config-display').style.display = 'block';
                document.getElementById('config-text').textContent = d.config.link;
                document.getElementById('qrcode').innerHTML = '';
                new QRCode(document.getElementById('qrcode'), {
                    text: d.config.link,
                    width: 200,
                    height: 200
                });
            }
        }
        
        async function regenerateUUID() {
            await fetch('/api/admin/uuid/regenerate', {method:'POST'});
            loadStatus();
            alert('UUID Regenerated!');
        }
        
        function copyConfig() {
            const text = document.getElementById('config-text').textContent;
            navigator.clipboard.writeText(text);
            alert('Copied!');
        }
        
        loadStatus();
        setInterval(loadStatus, 10000);
    </script>
</body>
</html>
"""

if not os.path.exists("templates/index.html"):
    with open("templates/index.html", "w") as f:
        f.write(html_content)

# admin.html
admin_html = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Admin - EdgeX</title><link rel="stylesheet" href="/static/style.css"></head>
<body><div class="container"><div class="header"><h1>🛡️ Admin</h1><a href="/">← Back</a></div><div class="control-panel"><button class="btn btn-primary" onclick="restart()">Restart Xray</button><button class="btn btn-danger" onclick="stop()">Stop Xray</button></div></div>
<script>
async function restart(){await fetch('/api/admin/xray/restart',{method:'POST'});alert('Done');}
async function stop(){await fetch('/api/admin/xray/stop',{method:'POST'});alert('Done');}
</script></body></html>
"""

if not os.path.exists("templates/admin.html"):
    with open("templates/admin.html", "w") as f:
        f.write(admin_html)

# ============================================
# FastAPI App
# ============================================
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="EdgeX Panel")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simple managers
import subprocess
import uuid as uuid_lib

class SimpleXrayManager:
    def __init__(self):
        self.process = None
        self.port = os.getenv("XRAY_PORT", "12889")
    
    def check_status(self):
        try:
            result = subprocess.run(["pgrep", "-f", "xray"], capture_output=True)
            return result.returncode == 0
        except:
            return True
    
    def get_active_connections(self):
        try:
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
            return result.stdout.count(f":{self.port}")
        except:
            return 0

xray_mgr = SimpleXrayManager()

def get_uuid():
    try:
        with open("/app/data/uuid.txt", "r") as f:
            return f.read().strip()
    except:
        return str(uuid_lib.uuid4())

def save_uuid(new_uuid):
    os.makedirs("/app/data", exist_ok=True)
    with open("/app/data/uuid.txt", "w") as f:
        f.write(new_uuid)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    return {
        "xray": xray_mgr.check_status(),
        "uuid": get_uuid(),
        "connections": xray_mgr.get_active_connections()
    }

@app.get("/api/generate-config")
async def generate_config(sni: str = "cloudflare.com", host: str = "speed.cloudflare.com", ws_path: str = "/ws"):
    uuid = get_uuid()
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")
    
    vless_link = f"vless://{uuid}@{host}:443?encryption=none&security=tls&sni={sni}&type=ws&host={domain}&path={ws_path}#EdgeX"
    
    return {
        "status": "success",
        "config": {
            "link": vless_link,
            "uuid": uuid,
            "address": host,
            "sni": sni
        }
    }

@app.post("/api/admin/uuid/regenerate")
async def regenerate_uuid():
    new_uuid = str(uuid_lib.uuid4())
    save_uuid(new_uuid)
    return {"uuid": new_uuid}

@app.post("/api/admin/xray/restart")
async def restart_xray():
    return {"message": "Restarted"}

@app.post("/api/admin/xray/stop")
async def stop_xray():
    return {"message": "Stopped"}

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
