from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
from xray_manager import XrayManager
from config_generator import ConfigGenerator
from uuid_manager import UUIDManager
from database import Database

app = FastAPI(title="EdgeX Panel", version="1.0.0")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Managers
xray_mgr = XrayManager()
config_gen = ConfigGenerator()
uuid_mgr = UUIDManager()
db = Database()

@app.on_event("startup")
async def startup():
    await db.init_db()
    print("✅ Database initialized")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    xray_status = xray_mgr.check_status()
    uuid = await uuid_mgr.get_active_uuid()
    return {
        "xray": xray_status,
        "uuid": uuid,
        "connections": xray_mgr.get_active_connections()
    }

@app.get("/api/generate-config")
async def generate_config(
    sni: str = "cloudflare.com",
    host: str = "speed.cloudflare.com",
    ws_path: str = "/ws"
):
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "example.railway.app")
    uuid = await uuid_mgr.get_active_uuid()
    
    config = config_gen.generate_vless_config(
        uuid=uuid,
        address=host,
        port=443,
        sni=sni,
        ws_path=ws_path,
        domain=domain,
        tcp_port=os.getenv("RAILWAY_TCP_PORT", "12889")
    )
    
    await db.save_config(config)
    
    return JSONResponse({
        "status": "success",
        "config": config
    })

@app.get("/api/logs")
async def get_logs():
    return {"logs": xray_mgr.get_logs(50)}

@app.post("/api/admin/uuid/regenerate")
async def regenerate_uuid():
    new_uuid = await uuid_mgr.regenerate_uuid()
    return {"uuid": new_uuid}

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
