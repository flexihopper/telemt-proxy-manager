#!/bin/bash

# Настройки для TeleMT
CONFIG_PATH="telemt_config/config.toml"

echo "=== Настройка TeleMT Proxy Manager ==="

if [ ! -f "$CONFIG_PATH" ]; then
    echo "❌ Ошибка: Файл $CONFIG_PATH не найден."
    echo "Сначала запустите: docker compose up -d"
    exit 1
fi

echo "✅ Файл конфигурации найден. Применяю настройки..."

# 1. Разрешаем доступ со всех IP (необходимо для Docker)
sed -i 's/whitelist = \["127.0.0.0\/8"\]/whitelist = ["0.0.0.0\/0"]/' "$CONFIG_PATH"

# 2. Устанавливаем пароль API (синхронно с менеджером)
sed -i 's/auth_header = ""/auth_header = "njxnjltkftnt"/' "$CONFIG_PATH"

# 3. Устанавливаем домен для маскировки (SNI)
sed -i 's/tls_domain = "petrovich.ru"/tls_domain = "ozon.ru"/' "$CONFIG_PATH"

# 4. Устанавливаем глобальный лимит: 1 IP на ключ
sed -i 's/user_max_unique_ips_global_each = 0/user_max_unique_ips_global_each = 1/' "$CONFIG_PATH"

echo "✅ Настройки успешно применены. Перезапускаю TeleMT..."
docker compose restart telemt

echo "🚀 Система готова к работе!"
