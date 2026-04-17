# Менеджер ключей TeleMT 🚀

Микросервис для управления пользователями прокси-сервера **TeleMT** (MTProxy на Rust) через REST API с автоматическим контролем времени жизни ключей.

## 🌟 Возможности

- **REST API (FastAPI)**: Создание, удаление и просмотр списка прокси-клачей.
- **Автоматическое удаление**: Гостевые ключи удаляются сами через 24 часа.
- **Надежный планировщик**: Использует **APScheduler** с базой **Redis**, что гарантирует удаление ключей даже после перезагрузки сервиса.
- **SQLite для данных**: Локальная база для отслеживания владельцев ключей.
- **Полная Docker-интеграция**: Готовый `docker-compose.yml`, который поднимает и прокси, и Redis.
- **Современный стек**: Python 3.12+, `uv`, асинхронный `SQLAlchemy` и красивые логи через `Loguru`.
- **Безопасность**: Защита эндпоинтов через API Key и режим `DEBUG` для скрытия документации.

## 🛠 Стек технологий

- **Фреймворк**: [FastAPI](https://fastapi.tiangolo.com/)
- **База данных**: SQLite с [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/)
- **Миграции**: [Alembic](https://alembic.sqlalchemy.org/)
- **Планировщик**: [APScheduler](https://apscheduler.readthedocs.io/)
- **Хранилище задач**: [Redis](https://redis.io/)
- **Логирование**: [Loguru](https://github.com/Delgan/loguru)
- **Окружение**: [uv](https://github.com/astral-sh/uv)

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/telemt-proxy-manager.git
cd telemt-proxy-manager
```

### 2. Настройте окружение

Скопируйте `.env.example` в `.env` и укажите свои данные:

```bash
cp .env.example .env
```

Основные настройки:

- `PROXY_HOST`: Публичный IP вашего сервера.
- `MANAGEMENT_API_KEY`: Секретный ключ для авторизации вашего бота в сервисе.

### 3. Запустите инфраструктуру

```bash
docker-compose up -d
```

### 4. Примените миграции базы данных

```bash
uv run alembic upgrade head
```

### 5. Настройте TeleMT

Скрипт автоматически откроет нужные порты и применит лимиты из вашего `.env`:

```bash
python3 configure_telemt.py
```

## 📖 Документация API

- **Swagger UI**: `http://localhost:8000/docs` (доступно, если `DEBUG=True`)
- **Основные эндпоинты**:
  - `POST /keys/guest`: Создать временный прокси-ключ (на 24 часа).
  - `POST /keys/permanent`: Создать постоянный ключ для конкретного Telegram ID.
  - `DELETE /keys/telegram/{tg_id}`: Отозвать доступ у пользователя.
  - `GET /keys/`: Список всех активных ключей.

---

Сделано с ❤️ для сообщества.
