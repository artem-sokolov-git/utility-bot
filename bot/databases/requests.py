from sqlalchemy import select

from bot.config import settings
from bot.databases.models import UserModel, async_session
from bot.domain.entities import UserMeta


async def auth_user(user_info: UserMeta) -> None:
    async with async_session() as session:
        is_admin = user_info.tg_id == settings.admin_id

        query = select(UserModel).where(UserModel.tg_id == user_info.tg_id)
        user = await session.scalar(query)

        if not user:
            user = UserModel(
                tg_id=user_info.tg_id,
                username=user_info.username,
                full_name=user_info.full_name,
                is_admin=is_admin,
            )
            session.add(user)
        else:
            user.username = user_info.username
            user.full_name = user_info.full_name
            user.is_admin = is_admin

        await session.commit()
