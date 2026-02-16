import sys
sys.path.insert(0, '.')
from app import db, create_app
from app.models import BackupLog, BackupConfig
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Очищаем старые данные
    BackupLog.query.delete()
    BackupConfig.query.delete()
    
    # Добавляем тестовые логи бэкапов
    statuses = ['success', 'failed', 'running']
    sheet_names = ['Salary Data', 'Employee Data', 'Financial Data']
    
    for i in range(20):
        status = statuses[i % 3]
        log = BackupLog(
            status=status,
            filename=f'backup_202402{str(i+1).zfill(2)}_120000.csv',
            sheet_name=sheet_names[i % 3],
            rows_count=100 + i * 10,
            duration=2.5 + i * 0.3,
            created_at=datetime.utcnow() - timedelta(days=i),
            error_message='Test error' if status == 'failed' else None
        )
        db.session.add(log)
    
    # Добавляем тестовые конфигурации
    configs = [
        ('BACKUP_SCHEDULE', '0 2 * * *', 'Ежедневно в 2:00'),
        ('RETENTION_DAYS', '30', 'Хранить бэкапы 30 дней'),
        ('EMAIL_NOTIFICATIONS', 'true', 'Включить уведомления'),
        ('GOOGLE_SHEET_ID', 'your-sheet-id-here', 'ID Google таблицы'),
        ('BACKUP_FORMATS', 'csv,json', 'Форматы бэкапа')
    ]
    
    for key, value, description in configs:
        config = BackupConfig(
            key=key,
            value=value,
            description=description
        )
        db.session.add(config)
    
    db.session.commit()
    print(f"✅ Created {BackupLog.query.count()} backup logs")
    print(f"✅ Created {BackupConfig.query.count()} config entries")
