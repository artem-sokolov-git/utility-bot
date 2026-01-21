from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from bot.config import settings
from bot.repositories.models import Base

engine: AsyncEngine = create_async_engine(
    url=settings.postgres_asyncpg_url,
    echo=settings.echo,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
