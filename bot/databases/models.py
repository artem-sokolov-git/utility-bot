from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bot.config import settings
from bot.databases.annotations import created_at, int_pk, str_255, updated_at

engine = create_async_engine(url=settings.postgres_asyncpg_url, echo=settings.echo)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        str_255: String(255),
    }


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class UserModel(BaseModel):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str_255 | None]
    full_name: Mapped[str_255 | None]
    is_admin: Mapped[bool] = mapped_column(default=False)


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
