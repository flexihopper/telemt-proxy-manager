# TeleMT Manager API Specification

Этот сервис управляет ключами для прокси-сервера TeleMT. Все запросы к API (кроме `/health`) требуют заголовок `X-API-Key`.

**Базовый URL:** `http://<your-server-ip>:8000`  
**Авторизация:** Заголовок `X-API-Key: super-secret-key-123` (измените в `.env`)

---

## Эндпоинты

### 1. Создание гостевого ключа

Создает анонимный ключ, который автоматически удалится через 24 часа.

- **URL:** `/keys/guest`
- **Метод:** `POST`
- **Ответ (200 OK):**

  ```json
  {
    "tg_user_id": null,
    "expires_at": "2026-04-17T20:20:09.971065Z",
    "id": 2,
    "username": "guest_9066a0ec",
    "secret": "fdb32d1deeb120638225172f12ec6314",
    "created_at": "2026-04-16T20:20:10.000000Z",
    "is_active": true,
    "proxy_url": "tg://proxy?server=IP&port=443&secret=ee..."
  }
  ```

### 2. Создание постоянного ключа

Создает бессрочный ключ, привязанный к Telegram ID пользователя. Если у пользователя уже был ключ, он будет заменен на новый.

- **URL:** `/keys/permanent`
- **Метод:** `POST`
- **Параметры (Query):** `tg_user_id` (integer)
- **Ответ (200 OK):** Аналогично гостевому, но `expires_at` будет `null`.

### 3. Удаление ключа по Telegram ID

Принудительное удаление доступа для конкретного пользователя.

- **URL:** `/keys/telegram/{tg_user_id}`
- **Метод:** `DELETE`
- **Ответ (200 OK):**

  ```json
  {
    "status": "ok",
    "message": "Key for user 12345 deleted"
  }
  ```

### 4. Список всех ключей

Получение списка всех активных ключей в системе.

- **URL:** `/keys/`
- **Метод:** `GET`
- **Ответ (200 OK):** Массив объектов ProxyKey.

---

## Формат ссылки (proxy_url)

Сервис автоматически генерирует ссылки в формате **MTProxy Fake TLS**:
`tg://proxy?server={HOST}&port={PORT}&secret=ee{SECRET}{DOMAIN_HEX}`
Где `ee` — префикс TLS, а в конце добавлен HEX-код домена (например, `google.com`).
