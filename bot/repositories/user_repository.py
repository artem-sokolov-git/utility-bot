from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repositories.models.user_model import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tg_id(self, tg_id: int) -> UserModel | None:
        query = select(UserModel).where(UserModel.tg_id == tg_id)
        return await self.session.scalar(query)

    async def create(
        self,
        tg_id: int,
        username: str | None,
        full_name: str | None,
        is_admin: bool = False,
    ) -> UserModel:
        user = UserModel(
            tg_id=tg_id,
            username=username,
            full_name=full_name,
            is_admin=is_admin,
        )
        self.session.add(user)
        return user

    async def update(
        self,
        user: UserModel,
        username: str | None,
        full_name: str | None,
        is_admin: bool,
    ) -> UserModel:
        user.username = username
        user.full_name = full_name
        user.is_admin = is_admin
        return user
