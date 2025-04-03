from __future__ import annotations

import asyncio

from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from models.entertainment import Entertainment
from repository.entertainment_repository import EntertainmentRepository


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


metadata = MetaData(schema='test')

entertainment_data = [
        {"price": 46840, "address": "Улица Гоголя, 12", "name": "Four Seasons", "type": "Отель", "rating": 5, 
                "check_in": datetime(2025, 3, 29, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)},
        {"price": 7340, "address": "Улица Толстого, 134", "name": "Мир", "type": "Хостел", "rating": 4, 
                "check_in": datetime(2025, 4, 2, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)}
    ]


@pytest_asyncio.fixture(scope="session")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionMaker() as session:
        await session.execute(text("SET search_path TO test"))
        await session.execute(text("TRUNCATE TABLE entertainment RESTART IDENTITY CASCADE"))
        for data in entertainment_data:
            await session.execute(text("INSERT INTO entertainment (price, address, name, type, rating, check_in, \
                check_out) VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out)"), data)
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    new_entertainment = Entertainment(entertainment_id=3, cost=33450, address="ул. Дмитриевского, 7",
            name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                                departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    await entertainment_repo.add(new_entertainment)

    result = await db_session.execute(text("SELECT * FROM entertainment ORDER BY id DESC LIMIT 1"))
    entertainment = result.mappings().first() 
    assert entertainment["name"] == "ABC"


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    existing_entertainment = Entertainment(entertainment_id=3, cost=46840, address="Улица Гоголя", name="Four Seasons", 
                            e_type="Отель", rating=5, entry_datetime=datetime(2025, 3, 29, 12, 30, 0), 
                                    departure_datetime=datetime(2025, 4, 5, 18, 0, 0))

    await entertainment_repo.add(existing_entertainment)
    
    result = await db_session.execute(text("SELECT * FROM entertainment WHERE type = :type"), 
                                                                {"type": "Отель"})
    entertainment = result.fetchone()
    
    assert entertainment is not None
    assert entertainment[4] == "Отель"


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    
    updated_entertainment = Entertainment(entertainment_id=1, cost=33450, address="ул. Дмитриевского, 7", 
                name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                            departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    await entertainment_repo.update(updated_entertainment)

    result = await db_session.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 1})
    entertainment = result.fetchone()

    assert entertainment is not None
    assert entertainment[3] == "ABC"
   

@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    non_existing_entertainment = Entertainment(entertainment_id=3, cost=33450, address="ул. Дмитриевского, 7", 
                    name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                                                departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    await entertainment_repo.update(non_existing_entertainment)
    
    result = await db_session.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 999})
    entertainment = result.fetchone()
    
    assert entertainment is None 


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    
    await entertainment_repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM entertainment"))
    entertainment = result.fetchone()

    assert 'Four Seasons' not in entertainment


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_not_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    
    await entertainment_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 999})
    entertainment = result.fetchone()
    
    assert entertainment is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    entertainment = await entertainment_repo.get_by_id(1)

    assert entertainment is not None
    assert entertainment.name == "Four Seasons"


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    entertainment = await entertainment_repo.get_by_id(12)

    assert entertainment is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    list_of_entertainment = await entertainment_repo.get_list()

    entertainment_names = [entertainment.e_type for entertainment in list_of_entertainment]
    expected_entertainment_names = [entertainment["type"] for entertainment in entertainment_data]
    
    entertainment_names.sort()
    expected_entertainment_names.sort()

    assert entertainment_names == expected_entertainment_names