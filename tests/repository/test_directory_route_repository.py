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
from models.directory_route import DirectoryRoute
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository


EXPECTED_CITY_ID = 6
EXPECTED_CITY_ID_P = 3
EXPECTED_CITY_ID_K = 5


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

metadata = MetaData(schema='test')

d_routes = [
        {"type_transport": "Паром", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 3987},
        {"type_transport": "Самолет", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 5123},
        {"type_transport": "Поезд", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 2541},
        {"type_transport": "Автобус", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 4756},
        {"type_transport": "Самолет", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 8322},
        {"type_transport": "Поезд", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 4305},
        {"type_transport": "Автобус", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 3796},
        {"type_transport": "Самолет", "departure_city": 5, "arrival_city": 4, "distance": 3025, "price": 10650},
        {"type_transport": "Поезд", "departure_city": 5, "arrival_city": 4, "distance": 3025, "price": 5988},
        {"type_transport": "Паром", "departure_city": 1, "arrival_city": 2, "distance": 515, "price": 13987},
        {"type_transport": "Самолет", "departure_city": 1, "arrival_city": 2, "distance": 467, "price": 2223},
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 2, "distance": 515, "price": 1911}
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
        await session.execute(text("TRUNCATE TABLE directory_route RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
        await session.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                        ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))
        for data in d_routes:
            await session.execute(text("INSERT INTO directory_route (type_transport, departure_city, \
                arrival_city, distance, price) \
            VALUES (:type_transport, :departure_city, :arrival_city, :distance, :price)"), data)
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    new_city = City(city_id=6, name="Новгород")
    await city_repo.add(new_city)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    new_city_from_db = await city_repo.get_by_id(6)
    assert new_city_from_db is not None

    departure_city = await city_repo.get_by_id(1)
    new_directory_route = DirectoryRoute(d_route_id=13, type_transport="Поезд", departure_city=departure_city, 
                                            destination_city=new_city_from_db, distance=445, cost=1234)
    await directory_route_repo.add(new_directory_route)

    result = await db_session.execute(text("SELECT * FROM directory_route ORDER BY id DESC LIMIT 1"))
    directory_route = result.fetchone()

    assert directory_route is not None
    assert directory_route[2] == 1
    assert directory_route[3] == EXPECTED_CITY_ID


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    existing_directory_route = DirectoryRoute(d_route_id=1, type_transport="Паром", 
        departure_city=await city_repo.get_by_id(3), destination_city=await city_repo.get_by_id(5), 
                                                                            distance=966, cost=3987)
    
    await directory_route_repo.add(existing_directory_route)
    
    result = await db_session.execute(text("SELECT * FROM directory_route WHERE id = :id"), 
                                                                {"id": 1})
    directory_route = result.fetchone()
    
    assert directory_route is not None
    assert directory_route[1] == 'Паром'


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    
    updated_directory_route = DirectoryRoute(d_route_id=1, type_transport="Паром", 
        departure_city=await city_repo.get_by_id(3), destination_city=await city_repo.get_by_id(5), 
                                                                            distance=966, cost=3987)
    await directory_route_repo.update(updated_directory_route)

    result = await db_session.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 1})
    directory_route = result.fetchone()

    assert directory_route is not None
    assert directory_route[1] == "Паром"
    assert directory_route.id == 1
    assert directory_route[2] == EXPECTED_CITY_ID_P
    assert directory_route[3] == EXPECTED_CITY_ID_K
   

@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    non_existing_directory_route = DirectoryRoute(d_route_id=999, type_transport="Паром", 
        departure_city=await city_repo.get_by_id(3), destination_city=await city_repo.get_by_id(5), 
                                                                            distance=966, cost=3987)

    await directory_route_repo.update(non_existing_directory_route)
    
    result = await db_session.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 999})
    directory_route = result.fetchone()
    
    assert directory_route is None 


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    
    await directory_route_repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 1})
    directory_route = result.fetchone()

    assert directory_route is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_not_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    
    await directory_route_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 999})
    directory_route = result.fetchone()
    
    assert directory_route is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    directory_route = await directory_route_repo.get_by_id(1)

    assert directory_route is not None
    assert directory_route.d_route_id == 1
    assert directory_route.departure_city is not None
    assert directory_route.destination_city is not None
    assert directory_route.departure_city.city_id == EXPECTED_CITY_ID_P
    assert directory_route.destination_city.city_id == EXPECTED_CITY_ID_K


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    directory_route = await directory_route_repo.get_by_id(132)

    assert directory_route is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_directory_route(db_session: AsyncSession) -> None:
    city_repo = CityRepository(db_session)
    directory_route_repo = DirectoryRouteRepository(db_session, city_repo)
    list_of_d_route = await directory_route_repo.get_list()

    for route, expected in zip(list_of_d_route, d_routes):
        assert route.type_transport == expected["type_transport"]
        assert route.departure_city is not None
        assert route.destination_city is not None
        assert route.departure_city.city_id == expected["departure_city"]
        assert route.destination_city.city_id == expected["arrival_city"]
        assert route.distance == expected["distance"]
        assert route.cost == expected["price"]

@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_cities_success(db_session: AsyncSession):
    city_repo = CityRepository(db_session)
    repo = DirectoryRouteRepository(db_session, city_repo)

    from_city_id = 3
    to_city_id = 4

    result: DirectoryRoute | None = await repo.get_by_cities(from_city_id, to_city_id)

    assert result is not None
    assert result.departure_city.city_id == from_city_id
    assert result.destination_city.city_id == to_city_id