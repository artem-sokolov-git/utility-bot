import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.start_service import auth_service

router = Router(name=__name__)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    try:
        await auth_service(message)
    except Exception as e:
        logging.error(f"Попытка авторизации вызвала ошибку: {e}")
