import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from api.keys import router as keys_router
from config import settings
from database import init_db
from services.scheduler import scheduler, start_scheduler

import logging

# Настройка логирования Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Очищаем старые настройки и ставим перехватчики
log_level = "DEBUG" if settings.DEBUG else "INFO"
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Устанавливаем уровни для сторонних библиотек, чтобы не шумели
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
    logging.getLogger(_log).handlers = [InterceptHandler()]

logger.remove()
logger.add(
    sys.stderr,
    level=log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up TeleMT API Service...")
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down TeleMT API Service...")
    if scheduler.running:
        scheduler.shutdown()


# Создаем приложение с учетом флага DEBUG
app = FastAPI(
    title="TeleMT Manager API",
    description="API for managing TeleMT proxy keys with automated expiration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.include_router(keys_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "debug": settings.DEBUG}
