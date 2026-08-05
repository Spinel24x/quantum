from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    is_admin: bool = False
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class ConfigRequest(BaseModel):
    sni: str = Field(default="cloudflare.com")
    host: str = Field(default="speed.cloudflare.com")
    ws_path: str = Field(default="/ws")
    
    @validator('ws_path')
    def validate_ws_path(cls, v):
        if not v.startswith('/'):
            v = '/' + v
        if len(v) < 2:
            raise ValueError('WebSocket path too short')
        return v

class UUIDResponse(BaseModel):
    uuid: str
    created_at: str
    active: bool

class SystemStatus(BaseModel):
    xray_running: bool
    panel_uptime: str
    active_connections: int
    version: str = "1.0.0"

class TrafficStats(BaseModel):
    upload: int = 0
    download: int = 0
    total: int = 0
