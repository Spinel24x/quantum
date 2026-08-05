import subprocess
import json
import os
import signal
import time
from pathlib import Path

class XrayManager:
    def __init__(self):
        self.config_path = "/etc/xray/config.json"
        self.xray_bin = "/opt/xray/xray"
        self.process = None
        self.port = os.getenv("XRAY_PORT", "12889")
    
    def generate_base_config(self, uuid: str):
        """تولید کانفیگ پایه Xray"""
        config = {
            "log": {
                "loglevel": "warning",
                "access": "/var/log/xray/access.log",
                "error": "/var/log/xray/error.log"
            },
            "inbounds": [{
                "port": int(self.port),
                "listen": "0.0.0.0",
                "protocol": "vless",
                "settings": {
                    "clients": [{
                        "id": uuid,
                        "level": 0,
                        "email": "default@edgex.panel"
                    }],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": {
                        "path": "/ws"
                    }
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"]
                }
            }],
            "outbounds": [{
                "protocol": "freedom",
                "tag": "direct"
            }],
            "routing": {
                "domainStrategy": "AsIs",
                "rules": []
            }
        }
        return config
    
    def save_config(self, config: dict):
        """ذخیره کانفیگ"""
        os.makedirs("/etc/xray", exist_ok=True)
        os.makedirs("/var/log/xray", exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def start(self):
        """شروع Xray"""
        if self.process:
            self.stop()
        
        self.process = subprocess.Popen(
            [self.xray_bin, "run", "-config", self.config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        
        return self.check_status()
    
    def stop(self):
        """توقف Xray"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    def restart(self):
        """ری‌استارت"""
        self.stop()
        return self.start()
    
    def check_status(self):
        """بررسی وضعیت"""
        if self.process:
            return self.process.poll() is None
        return False
    
    def get_active_connections(self):
        """اتصالات فعال"""
        try:
            result = subprocess.run(
                ["netstat", "-an", "|", "grep", f":{self.port}"],
                shell=True,
                capture_output=True,
                text=True
            )
            return len(result.stdout.strip().split('\n'))
        except:
            return 0
    
    def get_uptime(self):
        """مدت زمان اجرا"""
        if self.process:
            return time.time() - self.process._start_time if hasattr(self.process, '_start_time') else 0
        return 0
    
    async def update_config(self, config: dict):
        """آپدیت کانفیگ و ری‌استارت"""
        xray_config = self.generate_base_config(config['uuid'])
        
        # آپدیت WebSocket path
        if 'ws_path' in config:
            xray_config['inbounds'][0]['streamSettings']['wsSettings']['path'] = config['ws_path']
        
        self.save_config(xray_config)
        self.restart()
    
    def get_logs(self, lines: int = 50):
        """خوندن لاگ‌ها"""
        try:
            with open('/var/log/xray/access.log', 'r') as f:
                return f.readlines()[-lines:]
        except:
            return []
