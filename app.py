from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
import subprocess
import uuid as uuid_lib
from datetime import datetime
from pathlib import Path

# ============================================
# ساخت پوشه‌های مورد نیاز در زمان اجرا
# ============================================
Path("/app/static").mkdir(parents=True, exist_ok=True)
Path("/app/templates").mkdir(parents=True, exist_ok=True)
Path("/app/data").mkdir(parents=True, exist_ok=True)

# ============================================
# ساخت فایل CSS اگر وجود نداشته باشه
# ============================================
CSS_CONTENT = """
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --dark: #1e293b;
    --light: #f8fafc;
    --gray: #64748b;
    --border: #e2e8f0;
    --radius: 12px;
    --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: var(--dark);
}

.container {
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 900px;
    padding: 40px;
    animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.header {
    text-align: center;
    margin-bottom: 40px;
}

.header h1 {
    font-size: 2.5em;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary), #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.header .subtitle {
    color: var(--gray);
    font-size: 1.1em;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.status-card {
    background: linear-gradient(135deg, var(--light), white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    text-align: center;
    transition: transform 0.3s, box-shadow 0.3s;
}

.status-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow);
}

.status-card .icon {
    font-size: 2em;
    margin-bottom: 10px;
}

.status-card .label {
    color: var(--gray);
    font-size: 0.9em;
    margin-bottom: 5px;
}

.status-card .value {
    font-size: 1.5em;
    font-weight: 700;
    color: var(--dark);
}

.status-card .value.online {
    color: var(--secondary);
}

.status-card .value.offline {
    color: var(--danger);
}

.control-panel {
    background: var(--light);
    border-radius: var(--radius);
    padding: 30px;
    margin-bottom: 30px;
}

.control-panel h2 {
    margin-bottom: 20px;
    color: var(--dark);
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--dark);
}

.form-group input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--border);
    border-radius: 10px;
    font-size: 1em;
    transition: border-color 0.3s;
    background: white;
}

.form-group input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    font-size: 1em;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    width: 100%;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
}

.btn-danger {
    background: var(--danger);
    color: white;
    width: 100%;
    margin-top: 10px;
}

.btn-danger:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
}

.config-display {
    background: #1a1a2e;
    color: #00ff41;
    border-radius: var(--radius);
    padding: 20px;
    margin-top: 20px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    overflow-x: auto;
    position: relative;
    word-break: break-all;
}

.config-display .copy-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: var(--secondary);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.3s;
}

.config-display .copy-btn:hover {
    background: #059669;
}

.qr-section {
    text-align: center;
    margin-top: 20px;
}

#qrcode {
    display: inline-block;
    padding: 20px;
    background: white;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.log-section {
    background: var(--dark);
    color: #e2e8f0;
    border-radius: var(--radius);
    padding: 20px;
    margin-top: 20px;
    max-height: 300px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 20px;
    }
    
    .status-grid {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 2em;
    }
}

/* Toast notifications */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: white;
    padding: 16px 24px;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out;
    z-index: 1000;
}

.toast.success {
    border-left: 4px solid var(--secondary);
}

.toast.error {
    border-left: 4px solid var(--danger);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
"""

css_path = Path("/app/static/style.css")
if not css_path.exists():
    css_path.write_text(CSS_CONTENT)
    print("✅ CSS file created")

# ============================================
# ساخت فایل HTML اگر وجود نداشته باشه
# ============================================
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EdgeX Panel - Xray Management</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>⚡ EdgeX Panel</h1>
            <p class="subtitle">Professional Xray Configuration Manager</p>
        </div>

        <!-- Status Grid -->
        <div class="status-grid">
            <div class="status-card">
                <div class="icon">🟢</div>
                <div class="label">Xray Status</div>
                <div class="value" id="xray-status">Checking...</div>
            </div>
            <div class="status-card">
                <div class="icon">⏱️</div>
                <div class="label">Uptime</div>
                <div class="value" id="uptime">Running</div>
            </div>
            <div class="status-card">
                <div class="icon">🔗</div>
                <div class="label">Active Connections</div>
                <div class="value" id="active-connections">0</div>
            </div>
            <div class="status-card">
                <div class="icon">🔑</div>
                <div class="label">Current UUID</div>
                <div class="value" id="current-uuid" style="font-size: 0.8em;">Loading...</div>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <h2>⚙️ Configuration Generator</h2>
            
            <div class="form-group">
                <label for="sni-input">SNI (Server Name Indication):</label>
                <input type="text" id="sni-input" value="cloudflare.com" placeholder="e.g., cloudflare.com">
            </div>

            <div class="form-group">
                <label for="host-input">Host (Clean IP / Domain):</label>
                <input type="text" id="host-input" value="speed.cloudflare.com" placeholder="e.g., 1.1.1.1 or speed.cloudflare.com">
            </div>

            <div class="form-group">
                <label for="ws-path-input">WebSocket Path:</label>
                <input type="text" id="ws-path-input" value="/ws" placeholder="e.g., /ws">
            </div>

            <button id="generate-config" class="btn btn-primary">
                🚀 Generate Configuration
            </button>

            <button id="regenerate-uuid" class="btn btn-danger">
                🔄 Regenerate UUID
            </button>
        </div>

        <!-- Configuration Display -->
        <div id="config-display" class="config-display" style="display: none;">
            <button id="copy-config" class="copy-btn">📋 Copy</button>
            <pre id="config-text"></pre>
        </div>

        <!-- QR Code Section -->
        <div class="qr-section">
            <h3>📱 Scan QR Code</h3>
            <div id="qrcode"></div>
        </div>

        <!-- JSON Config Display -->
        <div style="margin-top: 20px;">
            <h3>📄 Raw Configuration (JSON)</h3>
            <pre id="json-config" class="config-display" style="max-height: 200px; overflow-y: auto;"></pre>
        </div>
    </div>

    <script>
        // Global variables
        let currentConfig = null;

        // Load status on page load
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update Xray status
                const xrayStatus = document.getElementById('xray-status');
                xrayStatus.textContent = data.xray ? '🟢 Online' : '🔴 Offline';
                xrayStatus.className = 'value ' + (data.xray ? 'online' : 'offline');
                
                // Update connections
                document.getElementById('active-connections').textContent = data.connections || 0;
                
                // Update UUID
                if (data.uuid) {
                    document.getElementById('current-uuid').textContent = data.uuid.substring(0, 16) + '...';
                }
            } catch (error) {
                console.error('Error loading status:', error);
            }
        }

        // Generate configuration
        async function generateConfig() {
            const btn = document.getElementById('generate-config');
            btn.textContent = '⏳ Generating...';
            btn.disabled = true;

            const sni = document.getElementById('sni-input').value || 'cloudflare.com';
            const host = document.getElementById('host-input').value || 'speed.cloudflare.com';
            const wsPath = document.getElementById('ws-path-input').value || '/ws';

            try {
                const response = await fetch(`/api/generate-config?sni=${encodeURIComponent(sni)}&host=${encodeURIComponent(host)}&ws_path=${encodeURIComponent(wsPath)}`);
                const data = await response.json();

                if (data.status === 'success') {
                    currentConfig = data.config;
                    
                    // Display config link
                    document.getElementById('config-display').style.display = 'block';
                    document.getElementById('config-text').textContent = currentConfig.link;
                    
                    // Display JSON
                    document.getElementById('json-config').textContent = JSON.stringify(currentConfig, null, 2);
                    
                    // Generate QR Code
                    const qrContainer = document.getElementById('qrcode');
                    qrContainer.innerHTML = '';
                    new QRCode(qrContainer, {
                        text: currentConfig.link,
                        width: 256,
                        height: 256,
                        colorDark: '#1e293b',
                        colorLight: '#ffffff',
                        correctLevel: QRCode.CorrectLevel.H
                    });
                    
                    showToast('✅ Configuration generated successfully!', 'success');
                } else {
                    showToast('❌ Failed to generate configuration', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('❌ Error generating configuration', 'error');
            } finally {
                btn.textContent = '🚀 Generate Configuration';
                btn.disabled = false;
            }
        }

        // Regenerate UUID
        async function regenerateUUID() {
            const btn = document.getElementById('regenerate-uuid');
            btn.textContent = '⏳ Regenerating...';
            btn.disabled = true;

            try {
                const response = await fetch('/api/admin/uuid/regenerate', { method: 'POST' });
                const data = await response.json();
                
                document.getElementById('current-uuid').textContent = data.uuid.substring(0, 16) + '...';
                showToast('🔄 UUID regenerated successfully!', 'success');
                
                // Reload status
                loadStatus();
            } catch (error) {
                showToast('❌ Error regenerating UUID', 'error');
            } finally {
                btn.textContent = '🔄 Regenerate UUID';
                btn.disabled = false;
            }
        }

        // Copy config to clipboard
        async function copyConfig() {
            const configText = document.getElementById('config-text').textContent;
            
            try {
                await navigator.clipboard.writeText(configText);
                showToast('📋 Configuration copied to clipboard!', 'success');
            } catch (error) {
                // Fallback method
                const textarea = document.createElement('textarea');
                textarea.value = configText;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('📋 Configuration copied!', 'success');
            }
        }

        // Toast notification
        function showToast(message, type = 'info') {
            const existingToast = document.querySelector('.toast');
            if (existingToast) {
                existingToast.remove();
            }
            
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            loadStatus();
            setInterval(loadStatus, 10000); // Refresh every 10 seconds
            
            document.getElementById('generate-config').addEventListener('click', generateConfig);
            document.getElementById('regenerate-uuid').addEventListener('click', regenerateUUID);
            document.getElementById('copy-config').addEventListener('click', copyConfig);
        });
    </script>
</body>
</html>
"""

html_path = Path("/app/templates/index.html")
if not html_path.exists():
    html_path.write_text(HTML_CONTENT)
    print("✅ HTML template created")

# Admin HTML
ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EdgeX Panel - Admin</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Admin Panel</h1>
            <p class="subtitle">System Administration</p>
            <a href="/" style="color: var(--primary); text-decoration: none;">← Back to Dashboard</a>
        </div>

        <div class="control-panel">
            <h2>System Controls</h2>
            
            <button class="btn btn-primary" onclick="restartXray()" style="margin-bottom: 10px;">
                🔄 Restart Xray
            </button>
            
            <button class="btn btn-danger" onclick="stopXray()">
                ⏹️ Stop Xray
            </button>
        </div>

        <div class="control-panel">
            <h2>UUID Management</h2>
            <p>Active UUID: <code id="admin-uuid">Loading...</code></p>
            <button class="btn btn-primary" onclick="regenerateUUID()">
                🔄 Regenerate UUID
            </button>
        </div>
    </div>

    <script>
        async function restartXray() {
            const response = await fetch('/api/admin/xray/restart', { method: 'POST' });
            const data = await response.json();
            alert(data.message || 'Xray restarted');
        }

        async function stopXray() {
            if (confirm('Are you sure you want to stop Xray?')) {
                const response = await fetch('/api/admin/xray/stop', { method: 'POST' });
                const data = await response.json();
                alert(data.message || 'Xray stopped');
            }
        }

        async function regenerateUUID() {
            const response = await fetch('/api/admin/uuid/regenerate', { method: 'POST' });
            const data = await response.json();
            document.getElementById('admin-uuid').textContent = data.uuid;
            alert('UUID regenerated!');
        }

        // Load initial UUID
        fetch('/api/status')
            .then(r => r.json())
            .then(d => {
                document.getElementById('admin-uuid').textContent = d.uuid || 'Unknown';
            });
    </script>
</body>
</html>
"""

admin_path = Path("/app/templates/admin.html")
if not admin_path.exists():
    admin_path.write_text(ADMIN_HTML)
    print("✅ Admin template created")

# ============================================
# FastAPI Application
# ============================================
app = FastAPI(title="EdgeX Panel", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="/app/templates")

# ============================================
# Helper Functions
# ============================================

def get_uuid() -> str:
    """Get current UUID"""
    try:
        uuid_file = Path("/app/data/uuid.txt")
        if uuid_file.exists():
            return uuid_file.read_text().strip()
    except:
        pass
    
    # Generate new UUID if not exists
    new_uuid = str(uuid_lib.uuid4())
    save_uuid(new_uuid)
    return new_uuid

def save_uuid(new_uuid: str):
    """Save UUID to file"""
    uuid_file = Path("/app/data/uuid.txt")
    uuid_file.parent.mkdir(parents=True, exist_ok=True)
    uuid_file.write_text(new_uuid)

def check_xray_status() -> bool:
    """Check if Xray is running"""
    try:
        result = subprocess.run(["pgrep", "-f", "xray"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        # If pgrep fails, assume running since we started it
        return True

def get_active_connections() -> int:
    """Get number of active connections"""
    try:
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.stdout.count(":12889")
    except:
        return 0

def get_xray_logs(lines: int = 50) -> list:
    """Get recent Xray logs"""
    try:
        log_file = Path("/var/log/xray/access.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
    except:
        pass
    return ["No logs available"]

# ============================================
# API Routes
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🔧 Initializing EdgeX Panel...")
    
    # Ensure UUID exists
    uuid = get_uuid()
    print(f"✅ UUID: {uuid}")
    
    print("🚀 EdgeX Panel is ready!")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def api_status():
    """Get system status"""
    return JSONResponse({
        "xray": check_xray_status(),
        "uuid": get_uuid(),
        "connections": get_active_connections(),
        "uptime": "Running",
        "version": "1.0.0"
    })

@app.get("/api/generate-config")
async def api_generate_config(
    sni: str = "cloudflare.com",
    host: str = "speed.cloudflare.com",
    ws_path: str = "/ws"
):
    """Generate VLESS configuration"""
    
    # Get settings
    uuid = get_uuid()
    
    # Get Railway domain
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")
    tcp_port = os.getenv("RAILWAY_TCP_PORT", "12889")
    
    # Ensure ws_path starts with /
    if not ws_path.startswith('/'):
        ws_path = '/' + ws_path
    
    # Build VLESS link
    vless_link = (
        f"vless://{uuid}@{host}:443"
        f"?encryption=none"
        f"&security=tls"
        f"&sni={sni}"
        f"&alpn=h2,http/1.1"
        f"&type=ws"
        f"&host={railway_domain}"
        f"&path={ws_path}"
        f"#EdgeX-{railway_domain.split('.')[0]}"
    )
    
    # Build JSON config
    config_data = {
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": host,
                    "port": 443,
                    "users": [{
                        "id": uuid,
                        "encryption": "none",
                        "level": 0
                    }]
                }]
            },
            "streamSettings": {
                "network": "ws",
                "security": "tls",
                "tlsSettings": {
                    "serverName": sni,
                    "allowInsecure": False,
                    "alpn": ["h2", "http/1.1"]
                },
                "wsSettings": {
                    "path": ws_path,
                    "headers": {
                        "Host": railway_domain
                    }
                }
            },
            "tag": "proxy"
        }]
    }
    
    config_response = {
        "uuid": uuid,
        "address": host,
        "port": 443,
        "sni": sni,
        "ws_path": ws_path,
        "host": railway_domain,
        "link": vless_link,
        "json_config": json.dumps(config_data, indent=2),
        "qr_content": vless_link
    }
    
    return JSONResponse({
        "status": "success",
        "config": config_response
    })

@app.post("/api/admin/uuid/regenerate")
async def api_regenerate_uuid():
    """Regenerate UUID"""
    new_uuid = str(uuid_lib.uuid4())
    save_uuid(new_uuid)
    
    return JSONResponse({
        "status": "success",
        "uuid": new_uuid
    })

@app.post("/api/admin/xray/restart")
async def api_restart_xray():
    """Restart Xray"""
    try:
        subprocess.run(["pkill", "-f", "xray"], capture_output=True)
        subprocess.Popen(["/opt/xray/xray", "run", "-config", "/etc/xray/config.json"])
        return JSONResponse({"message": "Xray restarted successfully"})
    except Exception as e:
        return JSONResponse({"message": f"Error: {str(e)}"}, status_code=500)

@app.post("/api/admin/xray/stop")
async def api_stop_xray():
    """Stop Xray"""
    try:
        subprocess.run(["pkill", "-f", "xray"], capture_output=True)
        return JSONResponse({"message": "Xray stopped"})
    except Exception as e:
        return JSONResponse({"message": f"Error: {str(e)}"}, status_code=500)

@app.get("/api/logs")
async def api_get_logs():
    """Get Xray logs"""
    return JSONResponse({"logs": get_xray_logs()})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============================================
# Main entry point
# ============================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
