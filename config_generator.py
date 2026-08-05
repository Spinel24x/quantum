import json
import base64
from typing import Dict

class ConfigGenerator:
    def generate_vless_config(
        self,
        uuid: str,
        address: str,
        port: int,
        sni: str,
        ws_path: str,
        domain: str,
        tcp_port: str
    ) -> Dict:
        """تولید کانفیگ کامل VLESS"""
        
        # ساخت لینک VLESS
        vless_link = (
            f"vless://{uuid}@{address}:{port}"
            f"?encryption=none"
            f"&security=tls"
            f"&sni={sni}"
            f"&type=ws"
            f"&host={domain}"
            f"&path={ws_path}"
            f"#EdgeX-{domain}"
        )
        
        # کانفیگ JSON برای کلاینت‌ها
        config_json = {
            "outbounds": [{
                "protocol": "vless",
                "settings": {
                    "vnext": [{
                        "address": address,
                        "port": port,
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
                        "allowInsecure": False
                    },
                    "wsSettings": {
                        "path": ws_path,
                        "headers": {
                            "Host": domain
                        }
                    }
                },
                "tag": "proxy"
            }]
        }
        
        return {
            "uuid": uuid,
            "address": address,
            "port": port,
            "sni": sni,
            "ws_path": ws_path,
            "host": domain,
            "link": vless_link,
            "json_config": json.dumps(config_json, indent=2),
            "qr_content": vless_link
        }
