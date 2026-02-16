#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import BackupLog, BackupConfig

app = create_app()

with app.app_context():
    try:
        # Проверяем, что модели работают
        print("✅ BackupLog count:", BackupLog.query.count())
        print("✅ BackupConfig count:", BackupConfig.query.count())
        
        # Тестируем метод index() админки
        from app.admin import MyAdminIndexView
        admin_view = MyAdminIndexView()
        
        # Попробуем получить статистику как в index()
        stats = {
            'total_backups': BackupLog.query.count(),
            'successful_backups': BackupLog.query.filter_by(status='success').count(),
            'failed_backups': BackupLog.query.filter_by(status='failed').count(),
            'config_count': BackupConfig.query.count(),
            'recent_backups': BackupLog.query.order_by(BackupLog.created_at.desc()).limit(5).all()
        }
        
        print("\n✅ Статистика получена успешно:")
        print(f"   Всего бэкапов: {stats['total_backups']}")
        print(f"   Успешных: {stats['successful_backups']}")
        print(f"   Ошибок: {stats['failed_backups']}")
        print(f"   Конфигураций: {stats['config_count']}")
        print(f"   Последние бэкапы: {len(stats['recent_backups'])}")
        
        print("\n✅ Тест пройден! Проблема может быть в маршрутизации Flask-Admin.")
        
    except Exception as e:
        import traceback
        print("\n❌ Ошибка:")
        traceback.print_exc()
