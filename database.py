import aiosqlite
import os
from datetime import datetime
from passlib.hash import bcrypt
from typing import Optional

class Database:
    def __init__(self):
        self.db_path = "/app/data/edgex.db"
        self.conn = None
    
    async def init_db(self):
        """ایجاد دیتابیس و جداول"""
        os.makedirs("/app/data", exist_ok=True)
        
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        
        # ایجاد جداول
        await self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                traffic_used BIGINT DEFAULT 0,
                traffic_limit BIGINT DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                address TEXT NOT NULL,
                port INTEGER NOT NULL,
                sni TEXT,
                ws_path TEXT,
                host TEXT,
                config_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ip_address TEXT,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                disconnected_at TIMESTAMP,
                upload BIGINT DEFAULT 0,
                download BIGINT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        await self.conn.commit()
    
    async def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """ایجاد کاربر جدید"""
        try:
            password_hash = bcrypt.hash(password)
            await self.conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, password_hash, int(is_admin))
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    async def verify_user(self, username: str, password: str) -> Optional[dict]:
        """تایید کاربر"""
        cursor = await self.conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        user = await cursor.fetchone()
        
        if user and bcrypt.verify(password, user['password_hash']):
            # به‌روزرسانی آخرین لاگین
            await self.conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(), user['id'])
            )
            await self.conn.commit()
            return dict(user)
        
        return None
    
    async def get_user(self, username: str) -> Optional[dict]:
        """گرفتن اطلاعات کاربر"""
        cursor = await self.conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = await cursor.fetchone()
        return dict(user) if user else None
    
    async def save_config(self, config: dict) -> bool:
        """ذخیره کانفیگ"""
        try:
            # غیرفعال کردن کانفیگ‌های قبلی
            await self.conn.execute("UPDATE configs SET is_active = 0")
            
            # ذخیره کانفیگ جدید
            await self.conn.execute(
                """INSERT INTO configs 
                   (uuid, address, port, sni, ws_path, host, config_data, is_active) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (
                    config.get('uuid'),
                    config.get('address'),
                    config.get('port'),
                    config.get('sni'),
                    config.get('ws_path'),
                    config.get('host'),
                    config.get('json_config')
                )
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    async def get_active_config(self) -> Optional[dict]:
        """گرفتن کانفیگ فعال"""
        cursor = await self.conn.execute(
            "SELECT * FROM configs WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1"
        )
        config = await cursor.fetchone()
        return dict(config) if config else None
    
    async def get_all_users(self) -> list:
        """لیست همه کاربران"""
        cursor = await self.conn.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = await cursor.fetchall()
        return [dict(user) for user in users]
    
    async def update_traffic(self, user_id: int, upload: int, download: int):
        """به‌روزرسانی ترافیک"""
        await self.conn.execute(
            "UPDATE users SET traffic_used = traffic_used + ? + ? WHERE id = ?",
            (upload, download, user_id)
        )
        await self.conn.commit()
    
    async def get_stats(self) -> dict:
        """گرفتن آمار کلی"""
        cursor = await self.conn.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
        active_users = await cursor.fetchone()
        
        cursor = await self.conn.execute("SELECT COUNT(*) as total FROM connections WHERE disconnected_at IS NULL")
        active_connections = await cursor.fetchone()
        
        return {
            "active_users": active_users['total'],
            "active_connections": active_connections['total'],
            "uptime": "Running"
        }
    
    async def close(self):
        """بستن اتصال دیتابیس"""
        if self.conn:
            await self.conn.close()
