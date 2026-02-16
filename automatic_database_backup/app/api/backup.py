from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import time

api_bp = Blueprint('api', __name__)

@api_bp.route('/backup/test', methods=['GET'])
def test_backup():
    return jsonify({
        'success': True,
        'message': 'Backup API is working',
        'version': '1.0.0',
        'endpoints': [
            '/api/backup/test',
            '/api/backup/status',
            '/api/backup/run (POST)',
            '/api/system/info'
        ]
    })

@api_bp.route('/backup/status', methods=['GET'])
def get_backup_status():
    try:
        from app import db
        from app.models import BackupLog
        
        logs = BackupLog.query.order_by(BackupLog.created_at.desc()).limit(10).all()
        return jsonify({
            'success': True,
            'total_backups': BackupLog.query.count(),
            'recent_backups': [{
                'id': log.id,
                'status': log.status,
                'filename': log.filename,
                'sheet_name': log.sheet_name,
                'rows_count': log.rows_count,
                'duration': log.duration,
                'created_at': log.created_at.isoformat() if log.created_at else None
            } for log in logs]
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'total_backups': 0,
            'recent_backups': [],
            'note': f'Database connection: {str(e)[:100]}'
        })

@api_bp.route('/backup/run', methods=['GET', 'POST'])
def run_backup():
    try:
        from app import db
        from app.models import BackupLog
        from app.services.drive_service import DriveService
        from app.services.email_service import EmailService
        import gspread
        import csv
        import tempfile
        import os
        from datetime import datetime

        start_time = datetime.utcnow()
        
        # 1. Создаём запись в логе
        backup_log = BackupLog(
            status='running',
            filename='',
            sheet_name=current_app.config.get('GOOGLE_SHEET_NAME', 'Data'),
            created_at=start_time
        )
        db.session.add(backup_log)
        db.session.commit()
        
        # 2. Читаем данные из Google Таблицы
        credentials_path = current_app.config.get('GOOGLE_CREDENTIALS_PATH', 'credentials/google_credentials.json')
        gc = gspread.service_account(filename=credentials_path)
        sheet_id = current_app.config.get('GOOGLE_SHEET_ID')
        sheet_name = current_app.config.get('GOOGLE_SHEET_NAME', 'Data')
        
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        rows_count = len(data)
        
        # 3. Сохраняем в CSV
        filename = f'backup_{start_time.strftime("%Y%m%d_%H%M%S")}.csv'
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if data:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        # 4. Загружаем в Google Drive
        drive_url = ''
        drive_file_id = ''
        if current_app.config.get('BACKUP_TO_DRIVE', True):
            try:
                drive_service = DriveService()
                result = drive_service.upload_file(file_path, filename)
                drive_url = result['drive_url']
                drive_file_id = result['file_id']
                current_app.logger.info(f"Uploaded to Google Drive: {drive_url}")
            except Exception as e:
                current_app.logger.warning(f"Failed to upload to Drive: {e}")
        
        # 5. Обновляем лог
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        backup_log.status = 'success'
        backup_log.filename = filename
        backup_log.rows_count = rows_count
        backup_log.duration = duration
        backup_log.drive_url = drive_url
        backup_log.drive_file_id = drive_file_id
        backup_log.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        db.session.commit()
        
        # 6. Отправляем email
        try:
            EmailService.send_backup_report(
                success=True,
                details={
                    'log_id': backup_log.id,
                    'filename': filename,
                    'rows': rows_count,
                    'duration_sec': f"{duration:.2f}",
                    'google_drive_url': drive_url or 'Not uploaded'
                }
            )
        except Exception as e:
            current_app.logger.warning(f"Email notification failed: {e}")
        
        # 7. Удаляем временный файл (если не нужно хранить локально)
        if not current_app.config.get('KEEP_LOCAL_COPY', False) and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Backup completed successfully',
            'data': {
                'log_id': backup_log.id,
                'duration_seconds': duration,
                'rows_backed_up': rows_count,
                'filename': filename,
                'drive_url': drive_url,
                'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Backup failed: {str(e)}")
        try:
            # Пытаемся обновить статус ошибки в логе
            if 'backup_log' in locals():
                backup_log.status = 'failed'
                backup_log.error_message = str(e)[:500]
                db.session.commit()
        except:
            pass
            
        # Отправляем уведомление об ошибке
        try:
            from app.services.email_service import EmailService
            EmailService.send_error_notification(str(e))
        except:
            pass
            
        return jsonify({
            'success': False,
            'message': f'Backup failed: {str(e)}'
        }), 500

@api_bp.route('/system/info', methods=['GET'])
def system_info():
    import os
    import platform
    import socket
    
    return jsonify({
        'success': True,
        'system': {
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'cpu_count': os.cpu_count(),
            'working_directory': os.getcwd()
        },
        'service': {
            'name': 'Automatic Database Backup',
            'version': '1.0.0',
            'status': 'running',
            'start_time': datetime.utcnow().isoformat()
        }
    })
