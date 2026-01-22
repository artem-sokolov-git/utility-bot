from decimal import Decimal
from typing import TypeVar

from bot.repositories import ReadingsRepository
from bot.repositories.models import ElectricityReadingModel, GasReadingModel, UtilityReadingModel

T = TypeVar("T", bound=UtilityReadingModel)


class ReadingsService:
    def __init__(self, readings_repo: ReadingsRepository):
        self.repo = readings_repo

    async def calculate_consumption(self, instance: T) -> dict:
        previous = await self.repo.get_previous(instance.__class__, instance.created_at)

        if isinstance(instance, GasReadingModel):
            if not previous:
                return {
                    "date": instance.created_at.date(),
                    "real_consumption": instance.reading_value,
                    "fake_consumption": instance.fake_reading_value,
                    "real_previous": 0,
                    "fake_previous": 0,
                    "real_current": instance.reading_value,
                    "fake_current": instance.fake_reading_value,
                }

            return {
                "date": instance.created_at.date(),
                "real_consumption": instance.reading_value - previous.reading_value,
                "fake_consumption": instance.fake_reading_value - previous.fake_reading_value,
                "real_previous": previous.reading_value,
                "fake_previous": previous.fake_reading_value,
                "real_current": instance.reading_value,
                "fake_current": instance.fake_reading_value,
                "previous_date": previous.created_at,
            }

        elif isinstance(instance, ElectricityReadingModel):
            if not previous:
                return {
                    "date": instance.created_at.date(),
                    "consumption": instance.reading_value,
                    "previous": 0,
                    "current": instance.reading_value,
                }

            return {
                "date": instance.created_at.date(),
                "consumption": instance.reading_value - previous.reading_value,
                "previous": previous.reading_value,
                "current": instance.reading_value,
                "previous_date": previous.created_at,
            }

        return {}

    async def calculate_payment(self, instance: T) -> dict:
        consumption_data = await self.calculate_consumption(instance)

        if isinstance(instance, GasReadingModel):
            fake_consumption = consumption_data.get("fake_consumption", 0)
            gas_cost = Decimal(fake_consumption) * instance.unit_price
            total = gas_cost + instance.transportation_bill

            return {
                **consumption_data,
                "unit_price": instance.unit_price,
                "transportation_bill": instance.transportation_bill,
                "gas_cost": gas_cost,
                "total": total,
            }

        elif isinstance(instance, ElectricityReadingModel):
            consumption = consumption_data.get("consumption", 0)
            total = Decimal(consumption) * instance.unit_price

            return {
                **consumption_data,
                "unit_price": instance.unit_price,
                "total": total,
            }

        return {}

    async def get_statistics(self, model_class: type[T], limit: int = 12) -> dict:
        readings = await self.repo.get_all(model_class, limit=limit)

        if not readings:
            return {
                "count": 0,
                "average_consumption": 0,
                "total_consumption": 0,
                "total_paid": Decimal("0"),
                "average_payment": Decimal("0"),
                "period_start": None,
                "period_end": None,
            }

        total_consumption = 0
        total_paid = Decimal("0")

        for reading in readings:
            consumption_data = await self.calculate_consumption(reading)
            payment_data = await self.calculate_payment(reading)

            if isinstance(reading, GasReadingModel):
                total_consumption += consumption_data.get("fake_consumption", 0)
            else:
                total_consumption += consumption_data.get("consumption", 0)

            total_paid += payment_data.get("total", Decimal("0"))

        count = len(readings)

        return {
            "count": count,
            "average_consumption": total_consumption / count if count else 0,
            "total_consumption": total_consumption,
            "total_paid": total_paid,
            "average_payment": total_paid / count if count else Decimal("0"),
            "period_start": readings[-1].created_at if readings else None,
            "period_end": readings[0].created_at if readings else None,
        }
