import uuid
import os
import json
from datetime import datetime
from pathlib import Path

class UUIDManager:
    def __init__(self):
        self.data_dir = "/app/data"
        self.uuid_file = f"{self.data_dir}/uuids.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """اطمینان از وجود دایرکتوری داده"""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.uuid_file):
            self._init_uuid_file()
    
    def _init_uuid_file(self):
        """ایجاد فایل UUID اولیه"""
        initial_data = {
            "active_uuid": str(uuid.uuid4()),
            "history": [],
            "created_at": datetime.now().isoformat(),
            "last_rotated": None
        }
        self._save(initial_data)
    
    def _load(self):
        """بارگذاری داده‌ها"""
        with open(self.uuid_file, 'r') as f:
            return json.load(f)
    
    def _save(self, data):
        """ذخیره داده‌ها"""
        with open(self.uuid_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def get_active_uuid(self) -> str:
        """گرفتن UUID فعال"""
        data = self._load()
        return data['active_uuid']
    
    async def regenerate_uuid(self) -> str:
        """تولید UUID جدید"""
        data = self._load()
        old_uuid = data['active_uuid']
        new_uuid = str(uuid.uuid4())
        
        # ذخیره در تاریخچه
        data['history'].append({
            "uuid": old_uuid,
            "deactivated_at": datetime.now().isoformat(),
            "replaced_by": new_uuid
        })
        
        # به‌روزرسانی UUID فعال
        data['active_uuid'] = new_uuid
        data['last_rotated'] = datetime.now().isoformat()
        
        # نگه داشتن ۱۰ UUID آخر
        if len(data['history']) > 10:
            data['history'] = data['history'][-10:]
        
        self._save(data)
        return new_uuid
    
    async def list_uuids(self) -> list:
        """لیست تمام UUID ها"""
        data = self._load()
        return {
            "active": data['active_uuid'],
            "history": data['history']
        }
    
    async def validate_uuid(self, uuid_string: str) -> bool:
        """اعتبارسنجی UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
