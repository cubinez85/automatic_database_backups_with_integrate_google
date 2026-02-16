from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from flask import redirect, url_for, request, current_app
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from app import db

# Модель пользователя для аутентификации (упрощенная)
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Настройка аутентификации
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

# Кастомные ModelView с аутентификацией
class SecureModelView(ModelView):
    def is_accessible(self):
        # В продакшене здесь должна быть настоящая аутентификация
        # Для тестирования разрешаем всем или используем базовую аутентификацию
        return True  # TODO: Заменить на реальную аутентификацию
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login', next=request.url))

class BackupLogView(SecureModelView):
    """Админ-панель для логов бэкапов"""
    column_list = ('id', 'status', 'filename', 'sheet_name', 'rows_count', 'duration', 'created_at')
    column_searchable_list = ['filename', 'sheet_name', 'status']
    column_filters = ['status', 'created_at']
    column_sortable_list = ['created_at', 'duration', 'rows_count']
    page_size = 50
    can_create = False
    can_edit = False
    can_delete = True
    can_export = True
    
    column_labels = {
        'id': 'ID',
        'status': 'Статус',
        'filename': 'Имя файла',
        'sheet_name': 'Лист',
        'rows_count': 'Кол-во строк',
        'duration': 'Длительность (сек)',
        'created_at': 'Создан'
    }
    
    column_formatters = {
        'duration': lambda v, c, m, p: f"{m.duration:.2f}" if m.duration else "0.00",
        'created_at': lambda v, c, m, p: m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else ''
    }

class BackupConfigView(SecureModelView):
    """Админ-панель для конфигураций"""
    column_list = ('key', 'value', 'description', 'updated_at')
    column_searchable_list = ['key', 'description']
    column_filters = ['key']
    form_columns = ('key', 'value', 'description')
    can_create = True
    can_edit = True
    can_delete = True
    
    column_labels = {
        'key': 'Ключ',
        'value': 'Значение',
        'description': 'Описание',
        'updated_at': 'Обновлен'
    }

# Создаем кастомный индекс вью для админки
from flask_admin import AdminIndexView, expose

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self, *args, **kwargs):
        from app.models import BackupLog, BackupConfig
        stats = {
            'total_backups': BackupLog.query.count(),
            'successful_backups': BackupLog.query.filter_by(status='success').count(),
            'failed_backups': BackupLog.query.filter_by(status='failed').count(),
            'config_count': BackupConfig.query.count(),
            'recent_backups': BackupLog.query.order_by(BackupLog.created_at.desc()).limit(5).all()
        }
        return super(MyAdminIndexView, self).render('admin/index.html', stats=stats)
    
    @expose('/login', methods=['GET', 'POST'])
    def admin_login(self):
        # Упрощенная аутентификация для тестирования
        # В продакшене заменить на настоящую аутентификацию
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # TODO: Заменить на проверку из базы данных или .env
            if username == 'admin' and password == 'admin123':
                user = AdminUser(1)
                login_user(user)
                return redirect(url_for('admin.index'))
        
        return self.render('admin/login.html')
    
    @expose('/logout')
    def admin_logout(self):
        logout_user()
        return redirect(url_for('admin.index'))

def init_admin(app):
    """Инициализация Flask-Admin"""
    try:
        # Инициализируем логин менеджер
        login_manager.init_app(app)
        login_manager.login_view = 'admin.admin_login'
        
        # Создаем админку с кастомным индексом
        admin = Admin(
            app, 
            name='Backup System Admin',
            template_mode='bootstrap3',
            index_view=MyAdminIndexView(),
            endpoint='admin'
        )
        
        # Добавляем модели
        from app.models import BackupLog, BackupConfig
        
        admin.add_view(BackupLogView(BackupLog, db.session, name='Логи бэкапов', category='Данные'))
        admin.add_view(BackupConfigView(BackupConfig, db.session, name='Конфигурации', category='Данные'))
        
        # Добавляем кастомные ссылки в меню
        admin.add_link(MenuLink(name='Вернуться на сайт', url='/'))
        admin.add_link(MenuLink(name='Запустить бэкап', url='/api/backup/run'))
        admin.add_link(MenuLink(name='API Документация', url='/api/backup/test'))
        
        app.logger.info("✅ Flask-Admin initialized successfully")
        
        # Создаем шаблоны если их нет
        create_admin_templates(app)
        
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize Flask-Admin: {e}")
        import traceback
        traceback.print_exc()

def create_admin_templates(app):
    """Создание кастомных шаблонов для админки"""
    import os
    templates_dir = os.path.join(app.root_path, 'templates', 'admin')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Создаем кастомный index.html
    index_template = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(index_template):
        with open(index_template, 'w') as f:
            f.write('''
{% extends 'admin/master.html' %}
{% block body %}
<div class="container">
    <h1>📊 Backup System Dashboard</h1>
    <hr>
    
    <div class="row">
        <div class="col-md-3">
            <div class="card text-white bg-primary mb-3">
                <div class="card-header">Всего бэкапов</div>
                <div class="card-body">
                    <h2 class="card-title">{{ stats.total_backups }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-success mb-3">
                <div class="card-header">Успешных</div>
                <div class="card-body">
                    <h2 class="card-title">{{ stats.successful_backups }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-danger mb-3">
                <div class="card-header">Ошибок</div>
                <div class="card-body">
                    <h2 class="card-title">{{ stats.failed_backups }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-info mb-3">
                <div class="card-header">Конфигураций</div>
                <div class="card-body">
                    <h2 class="card-title">{{ stats.config_count }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h3>Последние бэкапы</h3>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Статус</th>
                                <th>Файл</th>
                                <th>Лист</th>
                                <th>Строк</th>
                                <th>Длительность</th>
                                <th>Создан</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for backup in stats.recent_backups %}
                            <tr>
                                <td>{{ backup.id }}</td>
                                <td>
                                    {% if backup.status == 'success' %}
                                    <span class="badge bg-success">Успех</span>
                                    {% elif backup.status == 'failed' %}
                                    <span class="badge bg-danger">Ошибка</span>
                                    {% else %}
                                    <span class="badge bg-warning">{{ backup.status }}</span>
                                    {% endif %}
                                </td>
                                <td>{{ backup.filename }}</td>
                                <td>{{ backup.sheet_name }}</td>
                                <td>{{ backup.rows_count }}</td>
                                <td>{{ "%.2f"|format(backup.duration) }}s</td>
                                <td>{{ backup.created_at.strftime('%Y-%m-%d %H:%M') if backup.created_at else '' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h3>Быстрые действия</h3>
                </div>
                <div class="card-body">
                    <a href="/api/backup/run" class="btn btn-primary" target="_blank">
                        <i class="glyphicon glyphicon-play"></i> Запустить бэкап
                    </a>
                    <a href="{{ url_for('backuplog.index_view') }}" class="btn btn-secondary">
                        <i class="glyphicon glyphicon-list"></i> Все логи
                    </a>
                    <a href="{{ url_for('backupconfig.index_view') }}" class="btn btn-secondary">
                        <i class="glyphicon glyphicon-cog"></i> Конфигурации
                    </a>
                    <a href="/health" class="btn btn-info" target="_blank">
                        <i class="glyphicon glyphicon-heart"></i> Проверить здоровье
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')
    
    # Создаем шаблон логина
    login_template = os.path.join(templates_dir, 'login.html')
    if not os.path.exists(login_template):
        with open(login_template, 'w') as f:
            f.write('''
{% extends 'admin/master.html' %}
{% block body %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card mt-5">
                <div class="card-header">
                    <h3 class="text-center">🔐 Вход в админ-панель</h3>
                </div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('admin.admin_login') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Имя пользователя</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Пароль</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Войти</button>
                        </div>
                    </form>
                    <hr>
                    <div class="text-center">
                        <p class="text-muted">
                            <small>
                                Для тестирования используйте:<br>
                                Логин: <code>admin</code><br>
                                Пароль: <code>admin123</code>
                            </small>
                        </p>
                        <a href="/" class="btn btn-link">Вернуться на сайт</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')
    
    app.logger.info(f"✅ Admin templates created in {templates_dir}")
