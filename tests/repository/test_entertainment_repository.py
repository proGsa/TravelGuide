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

entertainments_data = [
        {"duration": "4 часа", "address": "Главная площадь", "event_name": "Концерт", 
                                            "event_time": datetime(2025, 4, 10, 16, 0, 0)},
        {"duration": "3 часа", "address": "ул. Кузнецова, 4", "event_name": "Выставка", 
                                            "event_time": datetime(2025, 4, 5, 10, 0, 0)}
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
        for data in entertainments_data:
            await session.execute(text("INSERT INTO entertainment (duration, address, event_name, event_time) \
            VALUES (:duration, :address, :event_name, :event_time)"), data)
        await session.commit()
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    new_entertainment = Entertainment(entertainment_id=3, duration="2 часа", address="Красная площадь", 
                                            event_name="Музей", event_time=datetime(2025, 4, 2, 14, 0, 0))

    await entertainment_repo.add(new_entertainment)

    result = await db_session.execute(text("SELECT * FROM entertainment ORDER BY id DESC LIMIT 1"))
    entertainment = result.mappings().first() 
    assert entertainment["address"] == "Красная площадь"


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    existing_entertainment = Entertainment(entertainment_id=1, duration="4 часа", address="Главная площадь",
                                            event_name="Концерт", event_time=datetime(2025, 4, 10, 16, 0, 0))
    
    await entertainment_repo.add(existing_entertainment)
    
    result = await db_session.execute(text("SELECT * FROM entertainment WHERE duration = :duration"), 
                                                                {"duration": "4 часа"})
    entertainment = result.fetchone()
    
    assert entertainment is not None
    assert entertainment[2] == "Главная площадь"


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    
    updated_entertainment = Entertainment(entertainment_id=1, duration="2 часа", address="Главная площадь",
                                            event_name="Фестиваль", event_time=datetime(2025, 4, 2, 14, 0, 0))
    await entertainment_repo.update(updated_entertainment)

    result = await db_session.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 1})
    entertainment = result.fetchone()

    assert entertainment is not None
    assert entertainment[1] == "2 часа"
   

@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    non_existing_entertainment = Entertainment(entertainment_id=999, duration="2 часа", address="Главная площадь", 
                                                event_name="Фестиваль", event_time=datetime(2025, 4, 2, 14, 0, 0))
    
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

    assert '4 часа' not in entertainment


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
    assert entertainment.event_name == "Концерт"


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    entertainment = await entertainment_repo.get_by_id(12)

    assert entertainment is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_entertainment(db_session: AsyncSession) -> None:
    entertainment_repo = EntertainmentRepository(db_session)
    list_of_entertainments = await entertainment_repo.get_list()

    entertainment_names = [entertainments.event_name for entertainments in list_of_entertainments]
    expected_entertainment_names = [entertainment["event_name"] for entertainment in entertainments_data]
    
    entertainment_names.sort()
    expected_entertainment_names.sort()

    assert entertainment_names == expected_entertainment_names