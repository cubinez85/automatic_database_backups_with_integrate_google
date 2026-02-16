import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask import current_app

class DriveService:
    def __init__(self):
        self.folder_id = current_app.config.get('DRIVE_BACKUP_FOLDER_ID')
        if not self.folder_id:
            raise ValueError("DRIVE_BACKUP_FOLDER_ID не указан в конфигурации")
        
        self.service = self._get_drive_service()
        current_app.logger.info(f"✅ DriveService инициализирован (папка ID: {self.folder_id})")

    def _get_drive_service(self):
        creds = None
        token_path = 'credentials/token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                raise RuntimeError(
                    "Токен авторизации недействителен. Запустите скрипт get_token.py для получения нового токена."
                )

        return build('drive', 'v3', credentials=creds)

    def upload_file(self, file_path, filename=None):
        if not filename:
            filename = os.path.basename(file_path)

        current_app.logger.info(f"📤 Загрузка: {filename} → папка ID: {self.folder_id}")

        file_metadata = {
            'name': filename,
            'parents': [self.folder_id]
        }

        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()

        # Делаем файл доступным по ссылке
        self.service.permissions().create(
            fileId=file['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        current_app.logger.info(f"✅ Файл загружен: {file['id']}")

        return {
            'file_id': file['id'],
            'web_view_link': file.get('webViewLink', ''),
            'drive_url': f"https://drive.google.com/file/d/{file['id']}/view"
        }

    def list_backups(self):
        current_app.logger.info(f"📋 Список бэкапов в папке: {self.folder_id}")
        results = self.service.files().list(
            q=f"'{self.folder_id}' in parents and trashed=false",
            orderBy='modifiedTime desc',
            fields="files(id, name, modifiedTime, size)"
        ).execute()
        files = results.get('files', [])
        current_app.logger.info(f"📦 Найдено файлов: {len(files)}")
        return files
