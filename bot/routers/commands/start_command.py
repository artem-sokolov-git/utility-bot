import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import settings
from bot.domain.entities import UserMeta
from bot.repositories import UserRepository
from bot.repositories.db import async_session
from bot.services import AuthService

router = Router(name=__name__)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    try:
        user = UserMeta(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )

        if user.tg_id not in settings.all_allowed_users:
            logging.info(f"Бот отклонил запрос на вход пользователя {user.allow_name}:{user.tg_id}")
            await message.answer("Извините это частный канал. Обратитесь к администратору чтобы получить разрешение.")
            return

        async with async_session() as session:
            user_repo = UserRepository(session)
            auth_service = AuthService(user_repo)
            await auth_service.authenticate_user(user)
            await session.commit()
        logging.info(f"Бот поздоровался с пользователем {user.allow_name}:{user.tg_id}")
        await message.answer(f"Привет! {user.allow_name}. Чем могу помочь вам сегодня?")

    except Exception as e:
        logging.error(f"Попытка авторизации вызвала ошибку: {e}")
        await message.answer("Произошла ошибка при авторизации. Попробуйте позже.")
