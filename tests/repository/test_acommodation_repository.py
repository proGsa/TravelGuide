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

from models.accommodation import Accommodation
from repository.accommodation_repository import AccommodationRepository


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


metadata = MetaData(schema='test')

accommodations_data = [
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
        await session.execute(text("TRUNCATE TABLE accommodations RESTART IDENTITY CASCADE"))
        for data in accommodations_data:
            await session.execute(text("INSERT INTO accommodations (duration, address, event_name, event_time) \
            VALUES (:duration, :address, :event_name, :event_time)"), data)
        await session.commit()
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    new_accommodation = Accommodation(accommodation_id=3, duration="2 часа", location="Красная площадь", 
                                            a_type="Музей", datetime=datetime(2025, 4, 2, 14, 0, 0))

    await accommodation_repo.add(new_accommodation)

    result = await db_session.execute(text("SELECT * FROM accommodations ORDER BY id DESC LIMIT 1"))
    accommodation = result.mappings().first() 
    assert accommodation["address"] == "Красная площадь"


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    existing_accommodation = Accommodation(accommodation_id=1, duration="4 часа", location="Главная площадь",
                                            a_type="Концерт", datetime=datetime(2025, 4, 10, 16, 0, 0))
    
    await accommodation_repo.add(existing_accommodation)
    
    result = await db_session.execute(text("SELECT * FROM accommodations WHERE duration = :duration"), 
                                                                {"duration": "4 часа"})
    accommodation = result.fetchone()
    
    assert accommodation is not None
    assert accommodation[2] == "Главная площадь"


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    
    updated_accommodation = Accommodation(accommodation_id=1, duration="2 часа", location="Главная площадь",
                                            a_type="Фестиваль", datetime=datetime(2025, 4, 2, 14, 0, 0))
    await accommodation_repo.update(updated_accommodation)

    result = await db_session.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 1})
    accommodation = result.fetchone()

    assert accommodation is not None
    assert accommodation[1] == "2 часа"
   

@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    non_existing_accommodation = Accommodation(accommodation_id=999, duration="2 часа", location="Главная площадь", 
                                                a_type="Фестиваль", datetime=datetime(2025, 4, 2, 14, 0, 0))
    
    await accommodation_repo.update(non_existing_accommodation)
    
    result = await db_session.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 999})
    accommodation = result.fetchone()
    
    assert accommodation is None 


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    
    await accommodation_repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM accommodations"))
    accommodation = result.fetchone()

    assert '4 часа' not in accommodation


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_not_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    
    await accommodation_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 999})
    accommodation = result.fetchone()
    
    assert accommodation is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    accommodation = await accommodation_repo.get_by_id(1)

    assert accommodation is not None
    assert accommodation.a_type == "Концерт"


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    accommodation = await accommodation_repo.get_by_id(12)

    assert accommodation is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_accommodation(db_session: AsyncSession) -> None:
    accommodation_repo = AccommodationRepository(db_session)
    list_of_accommodations = await accommodation_repo.get_list()

    accommodation_names = [accommodations.a_type for accommodations in list_of_accommodations]
    expected_accommodation_names = [accommodation["event_name"] for accommodation in accommodations_data]
    
    accommodation_names.sort()
    expected_accommodation_names.sort()

    assert accommodation_names == expected_accommodation_names