import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import generate_proxy_url, settings
from database import get_db
from models import ProxyKey
from schemas import ProxyKeyResponse
from services.scheduler import delete_key_task, scheduler
from services.telemt_client import telemt_client

# Настройка заголовка для API Key
api_key_header = APIKeyHeader(name="X-API-Key")


async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.MANAGEMENT_API_KEY:
        logger.warning(f"Unauthorized access attempt with API Key: {api_key}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key


# Применяем проверку ключа ко всему роутеру
router = APIRouter(prefix="/keys", tags=["keys"], dependencies=[Depends(validate_api_key)])


async def _create_key_internal(
    db: AsyncSession,
    tg_user_id: Optional[int] = None,
    expires_at: Optional[datetime] = None,
    username_prefix: str = "user",
    max_unique_ips: Optional[int] = None,
) -> ProxyKey:
    """Внутренняя логика создания ключа"""

    if tg_user_id:
        existing_query = select(ProxyKey).where(ProxyKey.tg_user_id == tg_user_id)
        result = await db.execute(existing_query)
        existing_key = result.scalar_one_or_none()

        if existing_key:
            logger.info(f"Replacing existing key for user {tg_user_id} ({existing_key.username})")
            await telemt_client.delete_user(existing_key.username)
            await db.delete(existing_key)
            try:
                scheduler.remove_job(f"delete_{existing_key.username}")
            except Exception as e:
                logger.debug(f"No job found to remove for {existing_key.username}: {e}")

    username = f"{username_prefix}_{secrets.token_hex(4)}"
    secret = secrets.token_hex(16)

    try:
        # RFC3339 требует 'Z' в конце для UTC времени
        expires_str = expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") if expires_at else None
        await telemt_client.create_user(
            username=username,
            secret=secret,
            expiration_rfc3339=expires_str,
            max_unique_ips=max_unique_ips or 1,
        )
    except Exception as e:
        logger.error(f"TeleMT creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create key on TeleMT server") from e

    new_key = ProxyKey(username=username, secret=secret, tg_user_id=tg_user_id, expires_at=expires_at)
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    if expires_at:
        scheduler.add_job(
            delete_key_task,
            "date",
            run_date=expires_at,
            args=[username],
            id=f"delete_{username}",
            replace_existing=True,
        )
        logger.info(f"Scheduled deletion for {username} at {expires_at}")

    return new_key


@router.post("/guest", response_model=ProxyKeyResponse)
async def create_guest_key(db: AsyncSession = Depends(get_db)):
    """Создает анонимный гостевой ключ на 24 часа."""
    logger.info("Creating new guest key...")
    expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    key = await _create_key_internal(db, tg_user_id=None, expires_at=expires_at, username_prefix="guest")

    res = ProxyKeyResponse.model_validate(key)
    res.proxy_url = generate_proxy_url(key.username, key.secret)
    return res


@router.post("/permanent", response_model=ProxyKeyResponse)
async def create_permanent_key(tg_user_id: int, max_ips: int = 1, db: AsyncSession = Depends(get_db)):
    """Создает постоянный ключ для Telegram ID."""
    logger.info(f"Creating permanent key for user {tg_user_id} with max_ips={max_ips}...")
    key = await _create_key_internal(
        db, tg_user_id=tg_user_id, expires_at=None, username_prefix="perm", max_unique_ips=max_ips
    )

    res = ProxyKeyResponse.model_validate(key)
    res.proxy_url = generate_proxy_url(key.username, key.secret)
    return res


@router.delete("/telegram/{tg_user_id}")
async def delete_by_telegram_id(tg_user_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление ключа по TG ID"""
    logger.info(f"Request to delete key for user {tg_user_id}")
    query = select(ProxyKey).where(ProxyKey.tg_user_id == tg_user_id)
    result = await db.execute(query)
    key = result.scalar_one_or_none()

    if not key:
        logger.warning(f"Attempted to delete non-existent key for TG ID {tg_user_id}")
        raise HTTPException(status_code=404, detail="Key for this user not found")

    await telemt_client.delete_user(key.username)
    await db.delete(key)
    await db.commit()

    try:
        scheduler.remove_job(f"delete_{key.username}")
    except Exception:
        pass

    logger.success(f"Key for user {tg_user_id} successfully deleted")
    return {"status": "ok", "message": f"Key for user {tg_user_id} deleted"}


@router.get("/", response_model=list[ProxyKeyResponse])
async def list_keys(db: AsyncSession = Depends(get_db)):
    """Список всех ключей"""
    result = await db.execute(select(ProxyKey))
    keys = result.scalars().all()

    response = []
    for k in keys:
        res = ProxyKeyResponse.model_validate(k)
        res.proxy_url = generate_proxy_url(k.username, k.secret)
        response.append(res)
    return response
