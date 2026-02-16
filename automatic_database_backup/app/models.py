from datetime import datetime
from app import db

class BackupLog(db.Model):
    """Модель для хранения логов бэкапов"""
    __tablename__ = 'backup_logs'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    filename = db.Column(db.String(255))
    drive_file_id = db.Column(db.String(255))
    drive_url = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    sheet_name = db.Column(db.String(100))
    rows_count = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    duration = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'filename': self.filename,
            'drive_file_id': self.drive_file_id,
            'drive_url': self.drive_url,
            'file_size': self.file_size,
            'sheet_name': self.sheet_name,
            'rows_count': self.rows_count,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'error_message': self.error_message
        }

    def __repr__(self):
        return f'<BackupLog {self.id} {self.status}>'


class BackupConfig(db.Model):
    """Модель для хранения конфигураций бэкапов"""
    __tablename__ = 'backup_configs'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<BackupConfig {self.key}>'
