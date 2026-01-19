"""
User model
"""

from datetime import datetime, UTC
from .database import add_record, update_record, find_record, get_all_records


class User:
    def __init__(self, id=None, telegram_id=None, username=None, first_name=None,
                 last_name=None, is_admin=False, created_at=None):
        self.id = int(id) if id else None
        self.telegram_id = int(telegram_id) if telegram_id else None
        self.username = str(username) if username else ''
        self.first_name = str(first_name) if first_name else ''
        self.last_name = str(last_name) if last_name else ''
        self.is_admin = str(is_admin).lower() == 'true' if isinstance(is_admin, str) else bool(is_admin)
        self.created_at = str(created_at) if created_at else datetime.now(UTC).isoformat()
    
    def save(self):
        """Save user to Google Sheets"""
        data = {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': str(self.is_admin),
            'created_at': self.created_at
        }
        
        if self.id:
            data['id'] = self.id
            update_record('Users', self.id, data)
        else:
            result = add_record('Users', data)
            self.id = result['id']
        return self
    
    @staticmethod
    def get_by_telegram_id(telegram_id):
        """Get user by Telegram ID"""
        _, record = find_record('Users', 'telegram_id', telegram_id)
        if record:
            return User(**record)
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        _, record = find_record('Users', 'id', user_id)
        if record:
            return User(**record)
        return None
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or str(self.telegram_id)
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
