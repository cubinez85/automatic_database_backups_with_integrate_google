import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://backup_user:StrongPassword123!@localhost/backup_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '95.174.94.246')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'cubinez85@cubinez.ru')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', 'cubinez85@cubinez.ru')

    # Google Sheets
    GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '')
    GOOGLE_CREDENTIALS_PATH = os.environ.get('GOOGLE_CREDENTIALS_PATH', 'credentials/google_credentials.json')

    # Google Drive Backup Settings (OAuth)
    OAUTH_CREDENTIALS_PATH = os.environ.get('OAUTH_CREDENTIALS_PATH', 'credentials/oauth_credentials.json')
    DRIVE_BACKUP_FOLDER_ID = os.environ.get('DRIVE_BACKUP_FOLDER_ID')  # ← КРИТИЧЕСКИ ВАЖНО
    BACKUP_TO_DRIVE = os.environ.get('BACKUP_TO_DRIVE', 'true').lower() == 'true'
    KEEP_LOCAL_COPY = os.environ.get('KEEP_LOCAL_COPY', 'false').lower() == 'true'
    # Backup Settings
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', '0 2 * * *')
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
    BACKUP_FORMATS = os.environ.get('BACKUP_FORMATS', 'csv,excel,json').split(',')

    # Data Structure
    SHEET_COLUMNS = os.environ.get('SHEET_COLUMNS', 'year,month,position,salary').split(',')  # ← ИСПРАВЛЕНО: сразу список

    @staticmethod
    def init_app(app):
        pass

config = {
    'development': Config,
    'production': Config,
    'default': Config
}
