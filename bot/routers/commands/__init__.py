__all__ = ("router",)

from aiogram import Router

from bot.routers.commands.start_command import router as start_command_router

router = Router(name=__name__)

router.include_router(start_command_router)
