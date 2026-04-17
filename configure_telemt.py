import os
import re

def configure():
    # 1. Загружаем переменные из .env
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')

    # Если в .env нет ключей, используем дефолты
    tls_domain = env_vars.get('TLS_DOMAIN', 'ozon.ru')
    auth_header = env_vars.get('TELEMT_AUTH_HEADER', '') # По умолчанию пустой

    config_path = 'telemt_config/config.toml'
    if not os.path.exists(config_path):
        print(f"❌ Ошибка: {config_path} не найден. Сначала запустите: docker compose up -d")
        return

    print(f"🔍 Настраиваю {config_path}...")

    with open(config_path, 'r') as f:
        content = f.read()

    # 2. Делаем надежные замены через regex
    # Разрешаем доступ со всех IP для API
    content = re.sub(r'whitelist = \["127\.0\.0\.0/8"\]', 'whitelist = ["0.0.0.0/0"]', content)
    
    # Ставим домен для маскировки (пробуем petrovich или google, если они там есть)
    content = re.sub(r'tls_domain = ".*"', f'tls_domain = "{tls_domain}"', content)
    
    # Если в конфиге вообще нет auth_header или он пустой, а в .env есть - можем прописать (но пока оставляем по желанию)
    if auth_header:
        content = re.sub(r'auth_header = ".*"', f'auth_header = "{auth_header}"', content)

    with open(config_path, 'w') as f:
        f.write(content)

    print(f"✅ Готово! Параметры из .env применены.")
    print(f"   - Domain: {tls_domain}")
    
    # Перезапуск
    print("\n♻️ Перезапускаю контейнеры...")
    os.system("docker compose restart telemt")

if __name__ == "__main__":
    configure()
