from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).absolute().parent.parent


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    bot_token: SecretStr = Field(...)
    chat_id: int = Field(...)
    tz: str = Field(...)
    admin_id: int = Field(...)
    allowed_users: list[int] = Field(default_factory=list)

    @property
    def all_allowed_users(self) -> set[int]:
        return {self.admin_id, *self.allowed_users}


class SQLAlchemySettings(EnvBaseSettings):
    echo: bool = Field(...)


class PostgresSettings(EnvBaseSettings):
    postgres_host: str = Field(...)
    postgres_port: str = Field(...)
    postgres_db: str = Field(...)
    postgres_user: str = Field(...)
    postgres_password: SecretStr = Field(...)

    @property
    def postgres_asyncpg_url(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password.get_secret_value())
        return f"postgresql+asyncpg://{user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


class Settings(BotSettings, SQLAlchemySettings, PostgresSettings): ...


settings = Settings()
