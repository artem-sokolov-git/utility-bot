from textwrap import dedent

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.repositories import ReadingsRepository
from bot.repositories.db import async_session
from bot.repositories.models import ElectricityReadingModel, GasReadingModel
from bot.services import ReadingsService

router = Router(name=__name__)


def _format_gas_receipt(payment_data: dict) -> str:
    """Форматирует квитанцию по газу."""
    return dedent(f"""
        <b>Газ - {payment_data["date"]}</b>
        ---
        Показания: <code>{payment_data["fake_previous"]}</code> - <code>{payment_data["fake_current"]}</code>
        Потребление: <code>{payment_data["fake_consumption"]}</code>
        Цена за м³: <code>{payment_data["unit_price"]}</code>
        Стоимость газа: <code>{payment_data["gas_cost"]}</code>
        Транспортировка: <code>{payment_data["transportation_bill"]}</code>
        ---
        Итого: <code>{payment_data["total"]}</code>
    """)


def _format_electricity_receipt(payment_data: dict) -> str:
    """Форматирует квитанцию по электричеству."""
    return dedent(f"""
        <b>Электричество - {payment_data["date"]}</b>
        ---
        Показания: <code>{payment_data["previous"]}</code> - <code>{payment_data["current"]}</code>
        Потребление: <code>{payment_data["consumption"]}</code>
        Цена за кВт·ч: <code>{payment_data["unit_price"]}</code>
        ---
        Итого: <code>{payment_data["total"]}</code>
    """)


@router.message(Command("receipt"))
async def cmd_receipt(message: Message) -> None:
    async with async_session() as session:
        readings_repo = ReadingsRepository(session)
        readings_service = ReadingsService(readings_repo)

        latest_gas = await readings_repo.get_latest(GasReadingModel)
        if latest_gas is None:
            await message.answer("Нет показаний по газу")
        else:
            gas_payment = await readings_service.calculate_payment(latest_gas)
            await message.answer(_format_gas_receipt(gas_payment))

        latest_electricity = await readings_repo.get_latest(ElectricityReadingModel)
        if latest_electricity is None:
            await message.answer("Нет показаний по электричеству")
        else:
            electricity_payment = await readings_service.calculate_payment(latest_electricity)
            await message.answer(_format_electricity_receipt(electricity_payment))
