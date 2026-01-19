from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped

from bot.repositories.models.annotations import created_at, int_pk, str_255, updated_at


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        str_255: String(255),
    }


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
