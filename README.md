# TeleMT Proxy Manager 🚀

Stand-alone microservice for managing **TeleMT** (Rust-based MTProxy) users via a REST API with automated lifecycle management.

## 🌟 Features

- **REST API (FastAPI)**: Create, delete, and list proxy keys.
- **Automated Lifecycle**: Guest keys are automatically deleted after a specified duration (default: 24h).
- **Persistent Scheduling**: Uses **APScheduler** with **Redis** backend to ensure scheduled deletions survive service restarts.
- **SQLite Storage**: Local database for tracking keys and ownership.
- **Docker Ready**: Includes a `docker-compose.yml` that sets up both TeleMT and Redis.
- **Modern Tech Stack**: Built with Python 3.12+, `uv`, `SQLAlchemy` (async), and `Loguru` for beautiful logging.
- **Security**: Optional API Key protection and `DEBUG` mode to hide documentation in production.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite with [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Scheduler**: [APScheduler](https://apscheduler.readthedocs.io/)
- **Job Store**: [Redis](https://redis.io/)
- **Logging**: [Loguru](https://github.com/Delgan/loguru)
- **Environment**: [uv](https://github.com/astral-sh/uv)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/telemt-proxy-manager.git
cd telemt-proxy-manager
```

### 2. Configure environment

Copy `.env.example` to `.env` and adjust the values:

```bash
cp .env.example .env
```

Key settings:

- `PROXY_HOST`: Your server's public IP.
- `MANAGEMENT_API_KEY`: Secrets for bot-to-manager authentication.

### 3. Spin up infrastructure

```bash
docker-compose up -d
```

### 4. Run the API

Using `uv`:

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## 📖 API Documentation

- **Swagger UI**: `http://localhost:8000/docs` (only if `DEBUG=True`)
- **Main Endpoints**:
  - `POST /keys/guest`: Generate a temporary proxy link (24h).
  - `POST /keys/permanent`: Create a key linked to a Telegram ID.
  - `DELETE /keys/telegram/{tg_id}`: Revoke access for a user.
  - `GET /keys/`: List all active keys.

## 🔒 Security

- All requests must include the `X-API-Key` header.
- Set `DEBUG=False` in `.env` to disable Swagger/Redoc endpoints in a production environment.

## 🤝 Integration

This service is designed to be consumed by Telegram bots (like `DAOFamily`).
Simply send a `POST` request to `/keys/guest` and receive a ready-to-use `tg://proxy` link.

---

Built with ❤️ by [Your Name/Org]
