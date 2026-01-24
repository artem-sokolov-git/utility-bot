from decimal import Decimal

import pytest

from bot.repositories.models import ElectricityReadingModel, GasReadingModel
from bot.repositories.readings_repository import ReadingsRepository
from bot.services.readings_service import ReadingsService


@pytest.mark.asyncio
async def test_calculate_consumption_gas_first_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(
        GasReadingModel, reading_value=1500, unit_price=7.99, fake_reading_value=1400, transportation_bill=150.50
    )
    await db_session.commit()

    result = await service.calculate_consumption(reading)

    assert result["real_consumption"] == 1500
    assert result["fake_consumption"] == 1400
    assert result["real_previous"] == 0
    assert result["fake_previous"] == 0
    assert result["real_current"] == 1500
    assert result["fake_current"] == 1400
    assert result["date"] == reading.created_at.date()


@pytest.mark.asyncio
async def test_calculate_consumption_gas_with_previous(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create first reading
    previous = await repo.create(
        GasReadingModel, reading_value=1000, unit_price=7.99, fake_reading_value=900, transportation_bill=100
    )
    await db_session.commit()

    # Create second reading
    current = await repo.create(
        GasReadingModel, reading_value=1500, unit_price=7.99, fake_reading_value=1400, transportation_bill=150.50
    )
    await db_session.commit()

    result = await service.calculate_consumption(current)

    assert result["real_consumption"] == 500  # 1500 - 1000
    assert result["fake_consumption"] == 500  # 1400 - 900
    assert result["real_previous"] == 1000
    assert result["fake_previous"] == 900
    assert result["real_current"] == 1500
    assert result["fake_current"] == 1400
    assert result["date"] == current.created_at.date()
    assert result["previous_date"] == previous.created_at


@pytest.mark.asyncio
async def test_calculate_consumption_electricity_first_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=4.32)
    await db_session.commit()

    result = await service.calculate_consumption(reading)

    assert result["consumption"] == 2500
    assert result["previous"] == 0
    assert result["current"] == 2500
    assert result["date"] == reading.created_at.date()


@pytest.mark.asyncio
async def test_calculate_consumption_electricity_with_previous(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create first reading
    previous = await repo.create(ElectricityReadingModel, reading_value=2000, unit_price=4.32)
    await db_session.commit()

    # Create second reading
    current = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=4.32)
    await db_session.commit()

    result = await service.calculate_consumption(current)

    assert result["consumption"] == 500  # 2500 - 2000
    assert result["previous"] == 2000
    assert result["current"] == 2500
    assert result["date"] == current.created_at.date()
    assert result["previous_date"] == previous.created_at


@pytest.mark.asyncio
async def test_calculate_payment_gas_first_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(
        GasReadingModel,
        reading_value=1500,
        unit_price=Decimal("7.99"),
        fake_reading_value=1400,
        transportation_bill=Decimal("150.50"),
    )
    await db_session.commit()

    result = await service.calculate_payment(reading)

    expected_gas_cost = Decimal("1400") * Decimal("7.99")  # 11186.00
    expected_total = expected_gas_cost + Decimal("150.50")  # 11336.50

    assert result["gas_cost"] == expected_gas_cost
    assert result["total"] == expected_total
    assert result["unit_price"] == Decimal("7.99")
    assert result["transportation_bill"] == Decimal("150.50")
    assert result["fake_consumption"] == 1400


@pytest.mark.asyncio
async def test_calculate_payment_gas_with_previous(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create first reading
    await repo.create(
        GasReadingModel,
        reading_value=1000,
        unit_price=Decimal("7.99"),
        fake_reading_value=900,
        transportation_bill=Decimal("100"),
    )
    await db_session.commit()

    # Create second reading
    reading = await repo.create(
        GasReadingModel,
        reading_value=1500,
        unit_price=Decimal("7.99"),
        fake_reading_value=1400,
        transportation_bill=Decimal("150.50"),
    )
    await db_session.commit()

    result = await service.calculate_payment(reading)

    fake_consumption = 500  # 1400 - 900
    expected_gas_cost = Decimal("500") * Decimal("7.99")  # 3995.00
    expected_total = expected_gas_cost + Decimal("150.50")  # 4145.50

    assert result["fake_consumption"] == fake_consumption
    assert result["gas_cost"] == expected_gas_cost
    assert result["total"] == expected_total
    assert result["unit_price"] == Decimal("7.99")
    assert result["transportation_bill"] == Decimal("150.50")


@pytest.mark.asyncio
async def test_calculate_payment_electricity_first_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=Decimal("4.32"))
    await db_session.commit()

    result = await service.calculate_payment(reading)

    expected_total = Decimal("2500") * Decimal("4.32")  # 10800.00

    assert result["consumption"] == 2500
    assert result["total"] == expected_total
    assert result["unit_price"] == Decimal("4.32")


@pytest.mark.asyncio
async def test_calculate_payment_electricity_with_previous(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create first reading
    await repo.create(ElectricityReadingModel, reading_value=2000, unit_price=Decimal("4.32"))
    await db_session.commit()

    # Create second reading
    reading = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=Decimal("4.32"))
    await db_session.commit()

    result = await service.calculate_payment(reading)

    consumption = 500  # 2500 - 2000
    expected_total = Decimal("500") * Decimal("4.32")  # 2160.00

    assert result["consumption"] == consumption
    assert result["total"] == expected_total
    assert result["unit_price"] == Decimal("4.32")


@pytest.mark.asyncio
async def test_get_statistics_gas_empty(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    result = await service.get_statistics(GasReadingModel, limit=12)

    assert result["count"] == 0
    assert result["average_consumption"] == 0
    assert result["total_consumption"] == 0
    assert result["total_paid"] == Decimal("0")
    assert result["average_payment"] == Decimal("0")
    assert result["period_start"] is None
    assert result["period_end"] is None


@pytest.mark.asyncio
async def test_get_statistics_gas_single_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(
        GasReadingModel,
        reading_value=1500,
        unit_price=Decimal("7.99"),
        fake_reading_value=1400,
        transportation_bill=Decimal("150.50"),
    )
    await db_session.commit()

    result = await service.get_statistics(GasReadingModel, limit=12)

    # First reading has consumption = fake_reading_value (1400)
    expected_gas_cost = Decimal("1400") * Decimal("7.99")
    expected_total = expected_gas_cost + Decimal("150.50")

    assert result["count"] == 1
    assert result["average_consumption"] == 1400
    assert result["total_consumption"] == 1400
    assert result["total_paid"] == expected_total
    assert result["average_payment"] == expected_total
    assert result["period_start"] == reading.created_at
    assert result["period_end"] == reading.created_at


@pytest.mark.asyncio
async def test_get_statistics_gas_multiple_readings(db_session):
    """Test gas statistics with multiple readings."""
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create 3 readings
    readings = []
    for i in range(3):
        reading = await repo.create(
            GasReadingModel,
            reading_value=1000 + (i * 500),
            unit_price=Decimal("7.99"),
            fake_reading_value=900 + (i * 500),
            transportation_bill=Decimal("100"),
        )
        await db_session.commit()
        readings.append(reading)

    result = await service.get_statistics(GasReadingModel, limit=12)

    # First reading: consumption = 900 (fake_reading_value)
    # Second reading: consumption = 1400 - 900 = 500
    # Third reading: consumption = 1900 - 1400 = 500
    # Total consumption = 900 + 500 + 500 = 1900

    assert result["count"] == 3
    assert result["total_consumption"] == 1900
    assert result["average_consumption"] == 1900 / 3
    assert result["period_start"] == readings[0].created_at
    assert result["period_end"] == readings[2].created_at


@pytest.mark.asyncio
async def test_get_statistics_electricity_empty(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    result = await service.get_statistics(ElectricityReadingModel, limit=12)

    assert result["count"] == 0
    assert result["average_consumption"] == 0
    assert result["total_consumption"] == 0
    assert result["total_paid"] == Decimal("0")
    assert result["average_payment"] == Decimal("0")
    assert result["period_start"] is None
    assert result["period_end"] is None


@pytest.mark.asyncio
async def test_get_statistics_electricity_single_reading(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    reading = await repo.create(ElectricityReadingModel, reading_value=2500, unit_price=Decimal("4.32"))
    await db_session.commit()

    result = await service.get_statistics(ElectricityReadingModel, limit=12)

    expected_total = Decimal("2500") * Decimal("4.32")

    assert result["count"] == 1
    assert result["average_consumption"] == 2500
    assert result["total_consumption"] == 2500
    assert result["total_paid"] == expected_total
    assert result["average_payment"] == expected_total
    assert result["period_start"] == reading.created_at
    assert result["period_end"] == reading.created_at


@pytest.mark.asyncio
async def test_get_statistics_electricity_multiple_readings(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create 3 readings
    readings = []
    for i in range(3):
        reading = await repo.create(ElectricityReadingModel, reading_value=2000 + (i * 500), unit_price=Decimal("4.32"))
        await db_session.commit()
        readings.append(reading)

    result = await service.get_statistics(ElectricityReadingModel, limit=12)

    # First reading: consumption = 2000
    # Second reading: consumption = 2500 - 2000 = 500
    # Third reading: consumption = 3000 - 2500 = 500
    # Total consumption = 2000 + 500 + 500 = 3000

    assert result["count"] == 3
    assert result["total_consumption"] == 3000
    assert result["average_consumption"] == 1000
    assert result["period_start"] == readings[0].created_at
    assert result["period_end"] == readings[2].created_at


@pytest.mark.asyncio
async def test_get_statistics_with_limit(db_session):
    repo = ReadingsRepository(db_session)
    service = ReadingsService(repo)

    # Create 5 readings
    for i in range(5):
        await repo.create(ElectricityReadingModel, reading_value=1000 + (i * 100), unit_price=Decimal("4.32"))
        await db_session.commit()

    result = await service.get_statistics(ElectricityReadingModel, limit=3)

    # Should only process the 3 most recent readings
    assert result["count"] == 3
