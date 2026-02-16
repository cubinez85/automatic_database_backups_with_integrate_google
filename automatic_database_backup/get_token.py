from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import pickle
import os
import sys

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    token_path = 'credentials/token.pickle'
    
    # Загружаем существующий токен
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Обновляем токен, если он просрочен
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Токен обновлён")
        return

    # Если токена нет — запускаем авторизацию
    if not creds or not creds.valid:
        # Создаём поток авторизации для консольного режима
        flow = Flow.from_client_secrets_file(
            'credentials/oauth_credentials.json',
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # ← КЛЮЧЕВОЙ ПАРАМЕТР для консоли
        )
        
        # Генерируем URL для авторизации
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'  # Всегда запрашиваем refresh_token
        )
        
        print("\n" + "="*70)
        print("🔑 ШАГ 1: ОТКРОЙТЕ ССЫЛКУ В БРАУЗЕРЕ НА СВОЁМ КОМПЬЮТЕРЕ")
        print("="*70)
        print(f"\n{auth_url}\n")
        print("💡 Инструкция:")
        print("   1. Скопируйте ссылку выше")
        print("   2. Вставьте её в браузер на своём компьютере")
        print("   3. Авторизуйтесь под аккаунтом cubinez85@gmail.com")
        print("   4. Разрешите доступ к Google Drive")
        print("   5. Скопируйте ПОЛНЫЙ код подтверждения (начинается с '4/')")
        print("="*70)
        
        # Просим пользователя ввести код
        code = input("\n🔑 ШАГ 2: ВСТАВЬТЕ КОД ПОДТВЕРЖДЕНИЯ И НАЖМИТЕ ENTER:\n> ").strip()
        
        if not code:
            print("\n❌ Ошибка: код не введён")
            sys.exit(1)
        
        # Обмениваем код на токен
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Сохраняем токен
        os.makedirs('credentials', exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print("\n" + "="*70)
        print("✅ УСПЕШНО! Токен сохранён в credentials/token.pickle")
        print("="*70)
        print(f"📧 Аккаунт: {creds.id_token.get('email') if creds.id_token else 'неизвестно'}")
        print(f"🔄 Refresh token: {'да' if creds.refresh_token else 'нет (повторите с prompt=consent)'}")
        print("="*70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}", file=sys.stderr)
        print("\n💡 Возможные решения:")
        print("   • Убедитесь, что файл credentials/oauth_credentials.json существует")
        print("   • Проверьте, что в Google Cloud Console:")
        print("     - OAuth согласие настроено как 'Внешнее'")
        print("     - Ваш email добавлен в 'Тестовые пользователи'")
        print("   • Если ошибка 'invalid_grant' — удалите token.pickle и повторите")
        sys.exit(1)
