import pytest
import pytest_asyncio
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import Settings
from bot.repositories.models import Base
from bot.services.reminder_service import ReminderService


class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env.test", env_file_encoding="utf-8", extra="ignore")


test_settings = TestSettings()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        url=test_settings.postgres_asyncpg_url,
        echo=test_settings.echo,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncSession:  # type: ignore
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def mock_bot(mocker):
    bot = mocker.MagicMock()
    bot.send_message = mocker.AsyncMock()
    return bot


@pytest.fixture
def reminder_service(mock_bot):
    return ReminderService(mock_bot)