import pytest

from bot.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(db_session):
    repo = UserRepository(db_session)

    user = await repo.create(tg_id=123456, username="test_user", full_name="Test User", is_admin=False)
    await db_session.commit()

    assert user.tg_id == 123456
    assert user.username == "test_user"
    assert user.full_name == "Test User"
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_get_user_by_tg_id(db_session):
    repo = UserRepository(db_session)

    await repo.create(tg_id=789012, username="another_user", full_name="Another User")
    await db_session.commit()

    found_user = await repo.get_by_tg_id(789012)

    assert found_user is not None
    assert found_user.tg_id == 789012
    assert found_user.username == "another_user"


@pytest.mark.asyncio
async def test_get_nonexistent_user(db_session):
    repo = UserRepository(db_session)

    found_user = await repo.get_by_tg_id(999999)

    assert found_user is None


@pytest.mark.asyncio
async def test_update_user(db_session):
    repo = UserRepository(db_session)

    user = await repo.create(tg_id=111222, username="old_name", full_name="Old Name", is_admin=False)
    await db_session.commit()

    updated_user = await repo.update(user=user, username="new_name", full_name="New Name", is_admin=True)
    await db_session.commit()

    assert updated_user.username == "new_name"
    assert updated_user.full_name == "New Name"
    assert updated_user.is_admin is True
