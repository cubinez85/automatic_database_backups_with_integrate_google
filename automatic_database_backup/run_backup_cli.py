#!/usr/bin/env python
"""
CLI-скрипт для запуска бэкапа из cron
Использует встроенный тестовый клиент Flask для вызова эндпоинта /api/backup/run
"""
import sys
import os
sys.path.insert(0, '/var/www/automatic_database_backup')

from app import create_app

def main():
    app = create_app()
    
    with app.app_context():
        # Используем тестовый клиент Flask для вызова эндпоинта
        client = app.test_client()
        response = client.post('/api/backup/run')  # POST как в маршруте
        
        # Выводим результат в stdout (попадёт в лог)
        output = response.get_data(as_text=True)
        print(f"[{os.getenv('BACKUP_SCHEDULE', '0 2 * * *')}] Backup executed at {__import__('datetime').datetime.now().isoformat()}")
        print(output)
        
        # Выходим с кодом ошибки, если бэкап неуспешен
        if response.status_code != 200 or '"success":false' in output.lower():
            sys.exit(1)
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
