import sys
sys.path.insert(0, '.')
from app import create_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

app = create_app()
with app.app_context():
    creds_path = app.config['GOOGLE_CREDENTIALS_PATH']
    creds = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
    )
    service = build('drive', 'v3', credentials=creds)
    
    folder_id = app.config['DRIVE_BACKUP_FOLDER_ID']
    print(f"🔍 Проверка папки ID: {folder_id}")
    
    try:
        # Получаем метаданные папки
        folder = service.files().get(
            fileId=folder_id,
            fields='id,name,owners,permissions'
        ).execute()
        
        print(f"\n📁 Название: {folder['name']}")
        print(f"👑 Владельцы:")
        for owner in folder['owners']:
            print(f"   - {owner.get('emailAddress', 'неизвестно')} (тип: {owner.get('kind')})")
        
        print(f"\n👥 Доступ:")
        for perm in folder.get('permissions', []):
            email = perm.get('emailAddress', '—')
            role = perm.get('role', '—')
            type_ = perm.get('type', '—')
            print(f"   - {email:40s} | роль: {role:10s} | тип: {type_}")
            
    except Exception as e:
        print(f"\n❌ Ошибка доступа: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Папка не поделена с сервисным аккаунтом")
        print("   2. Неправильный ID папки")
        print("   3. Папка принадлежит сервисному аккаунту (у него нет квоты)")
