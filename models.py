from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from database import Base


class ProxyKey(Base):
    __tablename__ = "proxy_keys"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    secret = Column(String(32), nullable=False)
    tg_user_id = Column(Integer, index=True, nullable=True)  # ID пользователя из Telegram

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON, nullable=True)  # Дополнительная инфа от TeleMT

    def __repr__(self):
        return f"<ProxyKey(username='{self.username}', expires_at='{self.expires_at}')>"
