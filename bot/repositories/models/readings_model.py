from sqlalchemy.orm import Mapped

from bot.repositories.models.annotations import uah
from bot.repositories.models.base_model import BaseModel


class UtilityReadingModel(BaseModel):
    __abstract__ = True

    reading_value: Mapped[int]
    unit_price: Mapped[uah]


class GasReadingModel(UtilityReadingModel):
    __tablename__ = "gas_readings"

    fake_reading_value: Mapped[int]
    transportation_bill: Mapped[uah]


class ElectricityReadingModel(UtilityReadingModel):
    __tablename__ = "electricity_readings"
