from textwrap import dedent
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.config import settings


class ReminderService:
    def __init__(self, bot: Bot):
        self.config = settings
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.tz))

    def _remind_message(self) -> str:
        return dedent("""
        <b>Напоминание!</b>
        Пора передать показания счётчиков.
        Пожалуйста, пришлите фото счётчиков газа и электричества.
        """)

    async def send_reminder(self) -> None:
        await self.bot.send_message(chat_id=settings.chat_id, text=self._remind_message())

    async def start(self) -> None:
        self.scheduler.add_job(self.send_reminder, CronTrigger(day=1, hour=10, minute=0))
        self.scheduler.start()

    def stop(self) -> None:
        self.scheduler.shutdown()
