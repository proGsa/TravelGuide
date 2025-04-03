from __future__ import annotations

import asyncio

from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from models.city import City
from repository.city_repository import CityRepository


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

metadata = MetaData(schema='test')


@pytest_asyncio.fixture(scope="session")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionMaker() as session:
        await session.execute(text("SET search_path TO test"))
        await session.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
        await session.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                    ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    new_city = City(city_id=1, name="Рязань")

    await city_repo.add(new_city)

    result = await db_session.execute(text("SELECT * FROM city ORDER BY city_id DESC LIMIT 1"))
    city = result.mappings().first() 
    assert city["name"] == "Рязань"


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    existing_city = City(city_id=1, name="Москва")  
    
    await city_repo.add(existing_city)
    
    result = await db_session.execute(text("SELECT * FROM city WHERE name = :name"), {"name": "Москва"})
    city = result.fetchone()
    
    assert city is not None
    assert city[1] == "Москва"


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    
    updated_city = City(city_id=1, name="Адлер")
    await city_repo.update(updated_city)

    result = await db_session.execute(text("SELECT name FROM city WHERE city_id = :city_id"), {"city_id": 1})
    city = result.fetchone()

    assert city is not None
    assert city[0] == "Адлер"
   

@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    non_existing_city = City(city_id=999, name="Город")
    
    await city_repo.update(non_existing_city)
    
    result = await db_session.execute(text("SELECT * FROM city WHERE city_id = :city_id"), {"city_id": 999})
    city = result.fetchone()
    
    assert city is None 


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    
    await city_repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM city"))
    city = result.fetchone()

    assert 'Москва' not in city


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_not_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    
    await city_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM city WHERE city_id = :city_id"), {"city_id": 999})
    city = result.fetchone()
    
    assert city is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    city = await city_repo.get_by_id(1)

    assert city is not None
    assert city.name == "Москва"


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    city = await city_repo.get_by_id(12)

    assert city is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_city(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    list_of_cities = await city_repo.get_list()

    city_names = [city.name for city in list_of_cities]
    expected_city_names = ["Москва", "Воронеж", "Санкт-Петербург", "Екатеринбург", "Калининград"]
    
    city_names.sort()
    expected_city_names.sort()

    assert city_names == expected_city_names