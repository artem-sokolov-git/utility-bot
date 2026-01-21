from datetime import datetime
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repositories.models import UtilityReadingModel

T = TypeVar("T", bound=UtilityReadingModel)


class ReadingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_previous(self, model_class: type[T], current_datetime: datetime) -> T | None:
        result = await self.session.execute(
            select(model_class)
            .where(model_class.created_at < current_datetime)
            .order_by(model_class.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, model_class: type[T]) -> T | None:
        result = await self.session.execute(select(model_class).order_by(model_class.created_at.desc()).limit(1))
        return result.scalar_one_or_none()

    async def get_by_id(self, model_class: type[T], reading_id: int) -> T | None:
        result = await self.session.execute(select(model_class).where(model_class.id == reading_id))
        return result.scalar_one_or_none()

    async def get_all(self, model_class: type[T], limit: int | None = None) -> list[T]:
        query = select(model_class).order_by(model_class.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, model_class: type[T], **kwargs) -> T:
        instance = model_class(**kwargs)
        self.session.add(instance)
        return instance

    async def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
