from bot.config import settings
from bot.domain.entities import UserMeta
from bot.repositories import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @staticmethod
    def is_admin(tg_id: int) -> bool:
        return tg_id == settings.admin_id

    async def authenticate_user(self, user_info: UserMeta) -> None:
        is_admin = self.is_admin(user_info.tg_id)

        user = await self.user_repository.get_by_tg_id(user_info.tg_id)

        if not user:
            await self.user_repository.create(
                tg_id=user_info.tg_id,
                username=user_info.username,
                full_name=user_info.full_name,
                is_admin=is_admin,
            )
        else:
            await self.user_repository.update(
                user=user,
                username=user_info.username,
                full_name=user_info.full_name,
                is_admin=is_admin,
            )
