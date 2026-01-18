import logging

from aiogram.types import Message

from bot.config import settings
from bot.databases.requests import auth_user
from bot.domain.entities import UserMeta


async def auth_service(message: Message) -> Message:
    user = UserMeta(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    if user.tg_id not in settings.all_allowed_users:
        logging.info(f"Бот отклонил запрос на вход пользователя {user.allow_name}:{user.tg_id}")
        await message.answer("Извините это частный канал. Обратитесь к администратору чтобы получить разрешение.")
    else:
        await auth_user(user)
        logging.info(f"Бот поздоровался с пользователем {user.allow_name}:{user.tg_id}")
        await message.answer(f"Привет! {user.allow_name}. Чем могу помочь вам сегодня?")
