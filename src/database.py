from typing import Any

from sqlalchemy import (Boolean, Column, CursorResult, DateTime, Delete,
                        ForeignKey, Identity, Insert, Integer, LargeBinary,
                        MetaData, Select, String, Update, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

Base = declarative_base()
DATABASE_URL = str(settings.DATABASE_URL)
SYNC_DATABASE_URL = str(settings.SYNC_DATABASE_URL)

engine = create_async_engine(DATABASE_URL)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'auth_user'

    email = Column(String, nullable=False)
    id = Column(Integer, Identity(), primary_key=True)
    password = Column(LargeBinary, nullable=True)
    is_admin = Column(Boolean, server_default="false", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


class Token(Base):
    """Модель токена."""

    __tablename__ = 'auth_refresh_token'

    uuid = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


async def fetch_one(select_query: Select | Insert | Update) -> dict[str, Any] | None:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> list[dict[str, Any]]:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r._asdict() for r in cursor.all()]


async def execute(select_query: Insert | Update | Delete) -> None:
    async with engine.begin() as conn:
        await conn.execute(select_query)
