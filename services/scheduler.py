from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import delete

from config import settings
from database import async_session_maker
from models import ProxyKey
from services.telemt_client import telemt_client

jobstores = {
    "default": RedisJobStore(
        host=settings.REDIS_URL.split("//")[1].split(":")[0],
        port=int(settings.REDIS_URL.split(":")[2].split("/")[0]),
        db=int(settings.REDIS_URL.split("/")[-1]),
    )
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


async def delete_key_task(username: str):
    """Фоновая задача: удаление из TeleMT и из локальной SQLite"""
    logger.info(f"Scheduled task started: deleting expired key '{username}'")
    try:
        # 1. Удаляем в TeleMT
        telemt_res = await telemt_client.delete_user(username)

        # 2. Удаляем из нашей локальной базы
        async with async_session_maker() as session:
            query = delete(ProxyKey).where(ProxyKey.username == username)
            await session.execute(query)
            await session.commit()

        if telemt_res:
            logger.success(f"Expired key '{username}' successfully deleted everywhere")
        else:
            logger.warning(f"Key '{username}' deleted from DB, but TeleMT reported an issue")

    except Exception as e:
        logger.exception(f"Critical error in background deletion for '{username}': {e}")


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started with Redis jobstore")
