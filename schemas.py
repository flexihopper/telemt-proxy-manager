from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProxyKeyBase(BaseModel):
    tg_user_id: Optional[int] = None
    expires_at: Optional[datetime] = None


class ProxyKeyCreate(ProxyKeyBase):
    username: Optional[str] = None  # If None, generate random


class ProxyKeyUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ProxyKeyResponse(ProxyKeyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    secret: str
    created_at: datetime
    is_active: bool
    proxy_url: Optional[str] = None  # Calculated field: tg://proxy?server=...&port=...&secret=...
