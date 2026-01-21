import pytest

from bot.repositories.models import ElectricityReadingModel, GasReadingModel
from bot.repositories.readings_repository import ReadingsRepository


@pytest.mark.asyncio
async def test_create_gas_reading(db_session):
    repo = ReadingsRepository(db_session)

    reading = await repo.create(
        GasReadingModel, reading_value=1500, unit_price=7.99, fake_reading_value=1400, transportation_bill=150.50
    )
    await db_session.commit()

    assert reading.reading_value == 1500
    assert reading.unit_price == 7.99
    assert reading.fake_reading_value == 1400
    assert reading.transportation_bill == 150.50


@pytest.mark.asyncio
async def test_create_electricity_reading(db_session):
    repo = ReadingsRepository(db_session)

    reading = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=4.32)
    await db_session.commit()

    assert reading.reading_value == 2500
    assert reading.unit_price == 4.32


@pytest.mark.asyncio
async def test_get_latest_reading(db_session):
    repo = ReadingsRepository(db_session)

    await repo.create(
        GasReadingModel, reading_value=100, unit_price=7.99, fake_reading_value=90, transportation_bill=50
    )
    await db_session.commit()

    await repo.create(
        GasReadingModel, reading_value=200, unit_price=7.99, fake_reading_value=180, transportation_bill=50
    )
    await db_session.commit()

    await repo.create(
        GasReadingModel, reading_value=300, unit_price=7.99, fake_reading_value=270, transportation_bill=50
    )
    await db_session.commit()

    latest = await repo.get_latest(GasReadingModel)

    assert latest is not None
    assert latest.reading_value == 300


@pytest.mark.asyncio
async def test_get_all_with_limit(db_session):
    repo = ReadingsRepository(db_session)

    for i in range(1, 6):
        await repo.create(ElectricityReadingModel, reading_value=i * 100, unit_price=4.32)
        await db_session.commit()

    readings = await repo.get_all(ElectricityReadingModel, limit=3)

    assert len(readings) == 3
    assert readings[0].reading_value == 500
    assert readings[1].reading_value == 400
    assert readings[2].reading_value == 300


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    repo = ReadingsRepository(db_session)

    reading = await repo.create(
        GasReadingModel, reading_value=1000, unit_price=7.99, fake_reading_value=900, transportation_bill=100
    )
    await db_session.commit()

    found = await repo.get_by_id(GasReadingModel, reading.id)

    assert found is not None
    assert found.id == reading.id
    assert found.reading_value == 1000


@pytest.mark.asyncio
async def test_delete_reading(db_session):
    repo = ReadingsRepository(db_session)

    reading = await repo.create(ElectricityReadingModel, reading_value=500, unit_price=4.32)
    await db_session.commit()

    reading_id = reading.id

    await repo.delete(reading)
    await db_session.commit()

    found = await repo.get_by_id(ElectricityReadingModel, reading_id)
    assert found is None
