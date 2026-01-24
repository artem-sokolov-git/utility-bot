from zoneinfo import ZoneInfo

import pytest
from apscheduler.triggers.cron import CronTrigger

from bot.services.reminder_service import ReminderService


@pytest.mark.asyncio
async def test_reminder_service_initialization(mock_bot):
    service = ReminderService(mock_bot)

    assert service.bot is mock_bot
    assert service.config is not None
    assert service.scheduler is not None
    assert isinstance(service.scheduler.timezone, ZoneInfo)


@pytest.mark.asyncio
async def test_send_reminder(reminder_service, mock_bot):
    await reminder_service.send_reminder()

    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args

    assert call_args.kwargs["chat_id"] == reminder_service.config.chat_id
    assert "Напоминание!" in call_args.kwargs["text"]
    assert "показания счётчиков" in call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_remind_message_format(reminder_service):
    message = reminder_service._remind_message()

    assert "<b>Напоминание!</b>" in message
    assert "Пора передать показания счётчиков" in message
    assert "фото счётчиков газа и электричества" in message


@pytest.mark.asyncio
async def test_start_adds_job(reminder_service):
    await reminder_service.start()

    jobs = reminder_service.scheduler.get_jobs()
    assert len(jobs) == 1

    job = jobs[0]
    assert job.func == reminder_service.send_reminder
    assert isinstance(job.trigger, CronTrigger)

    reminder_service.stop()


@pytest.mark.asyncio
async def test_start_with_correct_trigger(reminder_service):
    await reminder_service.start()

    jobs = reminder_service.scheduler.get_jobs()
    job = jobs[0]
    trigger = job.trigger

    # Check trigger string representation instead of internal fields
    trigger_str = str(trigger)
    assert "day='1'" in trigger_str
    assert "hour='10'" in trigger_str
    assert "minute='0'" in trigger_str

    reminder_service.stop()


@pytest.mark.asyncio
async def test_stop_shuts_down_scheduler(reminder_service):
    await reminder_service.start()
    assert reminder_service.scheduler.running

    reminder_service.stop()


@pytest.mark.asyncio
async def test_scheduler_timezone(reminder_service):
    tz = reminder_service.scheduler.timezone

    assert isinstance(tz, ZoneInfo)
    assert str(tz) == reminder_service.config.tz


@pytest.mark.asyncio
async def test_send_reminder_failure(reminder_service, mock_bot):
    mock_bot.send_message.side_effect = Exception("Bot API error")

    with pytest.raises(Exception, match="Bot API error"):
        await reminder_service.send_reminder()


@pytest.mark.asyncio
async def test_multiple_start_calls(reminder_service):
    from apscheduler.schedulers import SchedulerAlreadyRunningError

    await reminder_service.start()
    jobs_count_1 = len(reminder_service.scheduler.get_jobs())
    assert jobs_count_1 == 1

    # Trying to start again should raise error
    with pytest.raises(SchedulerAlreadyRunningError):
        await reminder_service.start()

    reminder_service.stop()
