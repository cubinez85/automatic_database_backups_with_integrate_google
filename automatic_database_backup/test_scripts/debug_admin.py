#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from app import create_app
import logging

# Включаем подробное логирование
logging.basicConfig(level=logging.DEBUG)

app = create_app()

# Включаем режим отладки
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.app_context():
    # Тестируем создание админки
    try:
        from app.admin import init_admin, admin
        print("✅ Импортированы модули админки")
        
        # Попробуем инициализировать админку
        init_admin(app)
        print("✅ Flask-Admin инициализирован")
        
        # Проверяем зарегистрированные маршруты
        print("\n=== Зарегистрированные маршруты ===")
        for rule in app.url_map.iter_rules():
            if 'admin' in str(rule):
                print(f"{rule.endpoint:30s} {rule}")
        
    except Exception as e:
        import traceback
        print("\n❌ Ошибка при инициализации админки:")
        traceback.print_exc()

print("\n✅ Тест завершён")
