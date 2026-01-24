__all__ = ("router",)

from aiogram import Router

from bot.routers.commands.receipt_command import router as receipt_command_router
from bot.routers.commands.start_command import router as start_command_router

router = Router(name=__name__)

router.include_router(start_command_router)
router.include_router(receipt_command_router)
