from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
cors = CORS()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Фабрика приложения"""
    app = Flask(__name__)
    
    # Загрузка конфигурации
    try:
        from config import config
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
    except Exception as e:
        app.logger.error(f"Config error: {e}")
        # Базовая конфигурация
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://backup_user:StrongPassword123!@localhost/backup_db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
    
    # Для аутентификации
    app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.admin_login'
    
    # Основные роуты
    @app.route('/')
    def index():
        return 'Automatic Database Backup System v1.0'
    
    @app.route('/health')
    def health():
        return 'OK'
    
    @app.route('/admin/quick-access')
    def admin_quick():
        """Быстрый доступ к админке"""
        return '''
        <h1>Quick Admin Access</h1>
        <p><a href="/admin/">Admin Panel</a></p>
        <p><a href="/admin/login">Login</a></p>
        <p><a href="/api/backup/test">API Test</a></p>
        '''
    
    # Регистрация API Blueprint
    try:
        from app.api.backup import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        app.logger.info("✅ API Blueprint registered successfully")
    except ImportError as e:
        app.logger.warning(f"⚠️ Could not register API Blueprint: {e}")
        # Создаем fallback маршруты
        @app.route('/api/backup/test')
        def api_test_fallback():
            from flask import jsonify
            return jsonify({'success': True, 'message': 'API (fallback mode)'})
    
    # Настройка Flask-Admin
    try:
        from app.admin import init_admin
        init_admin(app)
        app.logger.info("✅ Flask-Admin initialized")
    except ImportError as e:
        app.logger.warning(f"Flask-Admin not configured: {e}")
    except Exception as e:
        app.logger.error(f"❌ Error initializing Flask-Admin: {e}")
        import traceback
        traceback.print_exc()
    
    return app

# Создаем application для WSGI
application = create_app()

if __name__ == '__main__':
    application.run(host='127.0.0.1', port=8000, debug=True)
