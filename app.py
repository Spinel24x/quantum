from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from datetime import datetime
from .xray_manager import XrayManager
from .config_generator import ConfigGenerator
from .uuid_manager import UUIDManager
from .database import Database, User

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
    """راه‌اندازی اولیه"""
    await db.init_db()
    
    # ساخت ادمین پیش‌فرض
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "changeme")
    
    if not await db.get_user(admin_user):
        await db.create_user(admin_user, admin_pass, is_admin=True)
        print(f"✅ Admin user created: {admin_user}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """صفحه اصلی"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    """وضعیت سیستم"""
    xray_status = xray_mgr.check_status()
    return {
        "xray": xray_status,
        "uptime": xray_mgr.get_uptime(),
        "connections": xray_mgr.get_active_connections()
    }

@app.get("/api/generate-config")
async def generate_config(
    sni: str = "cloudflare.com",
    host: str = "speed.cloudflare.com",
    ws_path: str = "/ws"
):
    """تولید کانفیگ کلاینت"""
    
    # تنظیمات از Railway
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "example.railway.app")
    tcp_port = os.getenv("RAILWAY_TCP_PORT", "12889")
    xray_port = os.getenv("XRAY_PORT", "12889")
    
    # خوندن UUID
    uuid = await uuid_mgr.get_active_uuid()
    
    # ساخت کانفیگ
    config = config_gen.generate_vless_config(
        uuid=uuid,
        address=host,  # IP تمیز Cloudflare
        port=443,
        sni=sni,
        ws_path=ws_path,
        domain=domain,
        tcp_port=tcp_port
    )
    
    # ذخیره تنظیمات
    await db.save_config(config)
    
    # ری‌استارت Xray با کانفیگ جدید
    await xray_mgr.update_config(config)
    
    return JSONResponse({
        "status": "success",
        "config": config,
        "config_url": f"vless://{config['link']}"
    })

@app.post("/api/admin/uuid/regenerate")
async def regenerate_uuid():
    """بازسازی UUID"""
    new_uuid = await uuid_mgr.regenerate_uuid()
    return {"uuid": new_uuid}

@app.get("/api/logs")
async def get_logs():
    """گرفتن لاگ‌ها"""
    logs = xray_mgr.get_logs(50)
    return {"logs": logs}

# Admin Routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

if __name__ == "__main__":
    port = int(os.getenv("PANEL_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
