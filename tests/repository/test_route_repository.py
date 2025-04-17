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

from models.city import City
from models.directory_route import DirectoryRoute
from models.route import Route
from models.travel import Travel
from repository.accommodation_repository import AccommodationRepository
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.route_repository import RouteRepository
from repository.travel_repository import TravelRepository
from repository.user_repository import UserRepository


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


metadata = MetaData(schema='test')

travels = [{"status": "В процессе", "user_id": 1}, {"status": "Завершен", "user_id": 1}]

accommodations_data = [
        {"price": 46840, "address": "Улица Гоголя, 12", "name": "Four Seasons", "type": "Отель", "rating": 5, 
                "check_in": datetime(2025, 3, 29, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)},
        {"price": 7340, "address": "Улица Толстого, 134", "name": "Мир", "type": "Хостел", "rating": 4, 
                "check_in": datetime(2025, 4, 2, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)}
    ]
entertainment_data = [
        {"duration": "4 часа", "address": "Главная площадь", "event_name": "Концерт", 
                                            "event_time": datetime(2025, 4, 10, 16, 0, 0)},
        {"duration": "3 часа", "address": "ул. Кузнецова, 4", "event_name": "Выставка", 
                                            "event_time": datetime(2025, 4, 5, 10, 0, 0)}
    ]

tr_ent = [(1, 2), (2, 1)]

tr_a = [(1, 1), (2, 2)]

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
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 2, "distance": 515, "price": 1911},
        {"type_transport": "Самолет", "departure_city": 1, "arrival_city": 4, "distance": 1780, "price": 7500},
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 4, "distance": 1780, "price": 3500},
        {"type_transport": "Автобус", "departure_city": 1, "arrival_city": 4, "distance": 1780, "price": 3200},
        {"type_transport": "Самолет", "departure_city": 1, "arrival_city": 3, "distance": 700, "price": 3200},
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 3, "distance": 700, "price": 1800},
        {"type_transport": "Автобус", "departure_city": 1, "arrival_city": 3, "distance": 700, "price": 1600},
        {"type_transport": "Самолет", "departure_city": 1, "arrival_city": 5, "distance": 1280, "price": 6200},
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 5, "distance": 1280, "price": 3100},
        {"type_transport": "Автобус", "departure_city": 1, "arrival_city": 5, "distance": 1280, "price": 2800},

        {"type_transport": "Паром", "departure_city": 5, "arrival_city": 3, "distance": 966, "price": 3987},
        {"type_transport": "Самолет", "departure_city": 5, "arrival_city": 3, "distance": 966, "price": 5123},
        {"type_transport": "Поезд", "departure_city": 5, "arrival_city": 3, "distance": 966, "price": 2541},
        {"type_transport": "Автобус", "departure_city": 5, "arrival_city": 3, "distance": 966, "price": 4756},
        {"type_transport": "Самолет", "departure_city": 4, "arrival_city": 3, "distance": 1840, "price": 8322},
        {"type_transport": "Поезд", "departure_city": 4, "arrival_city": 3, "distance": 1840, "price": 4305},
        {"type_transport": "Автобус", "departure_city": 4, "arrival_city": 3, "distance": 1840, "price": 3796},
        {"type_transport": "Самолет", "departure_city": 4, "arrival_city": 5, "distance": 3025, "price": 10650},
        {"type_transport": "Поезд", "departure_city": 4, "arrival_city": 5, "distance": 3025, "price": 5988},
        {"type_transport": "Паром", "departure_city": 2, "arrival_city": 1, "distance": 515, "price": 13987},
        {"type_transport": "Самолет", "departure_city": 2, "arrival_city": 1, "distance": 467, "price": 2223},
        {"type_transport": "Поезд", "departure_city": 2, "arrival_city": 1, "distance": 515, "price": 1911},
        {"type_transport": "Самолет", "departure_city": 4, "arrival_city": 1, "distance": 1780, "price": 7500},
        {"type_transport": "Поезд", "departure_city": 4, "arrival_city": 1, "distance": 1780, "price": 3500},
        {"type_transport": "Автобус", "departure_city": 4, "arrival_city": 1, "distance": 1780, "price": 3200},
        {"type_transport": "Самолет", "departure_city": 3, "arrival_city": 1, "distance": 700, "price": 3200},
        {"type_transport": "Поезд", "departure_city": 3, "arrival_city": 1, "distance": 700, "price": 1800},
        {"type_transport": "Автобус", "departure_city": 3, "arrival_city": 1, "distance": 700, "price": 1600},
        {"type_transport": "Самолет", "departure_city": 5, "arrival_city": 1, "distance": 1280, "price": 6200},
        {"type_transport": "Поезд", "departure_city": 5, "arrival_city": 1, "distance": 1280, "price": 3100},
        {"type_transport": "Автобус", "departure_city": 5, "arrival_city": 1, "distance": 1280, "price": 2800}
    ]

route = [
    {"d_route_id": 1, "travel_id": 1, "start_time": datetime(2025, 4, 2, 7, 30, 0),
                                     "end_time": datetime(2025, 4, 6, 7, 0, 0)}, 
    {"d_route_id": 9, "travel_id": 1, "start_time": datetime(2025, 4, 3, 7, 30, 0),
                                     "end_time": datetime(2025, 4, 6, 7, 0, 0)},
    {"d_route_id": 11, "travel_id": 2, "start_time": datetime(2025, 3, 29, 6, 50, 0), 
                                        "end_time": datetime(2025, 4, 5, 22, 45, 0)}
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
        await session.execute(text("TRUNCATE TABLE travel_accommodations RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE travel_entertainment RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE accommodations RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE entertainment RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE travel RESTART IDENTITY CASCADE"))

        await session.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE directory_route RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE route RESTART IDENTITY CASCADE"))

        await session.execute(text("""
                INSERT INTO users (full_name, passport, phone, email, username, password)
                VALUES 
                ('Лобач Анастасия Олеговна', '1111111111', '89261111111', 'nastya@lobach.info', 'user1', '123!e5T78')
            """))

        for data in accommodations_data:
            await session.execute(text("INSERT INTO accommodations (price, address, name, type, rating, check_in, \
                 check_out) VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out)"), data)
        for data in entertainment_data:
            await session.execute(text("INSERT INTO entertainment (duration, address, event_name, event_time) \
                VALUES (:duration, :address, :event_name, :event_time)"), data)
        for data in travels:
            await session.execute(text("INSERT INTO travel (status, user_id) \
                VALUES (:status, :user_id)"), data)
        for t_a in tr_a:
            await session.execute(
                    text("INSERT INTO travel_entertainment (travel_id, entertainment_id) \
                        VALUES (:travel_id, :entertainment_id)"), 
                        {
                            "travel_id": t_a[0],
                            "entertainment_id": t_a[1]
                        }
                )
        for t_e in tr_ent:
            await session.execute(
                    text("INSERT INTO travel_accommodations (travel_id, accommodation_id) \
                        VALUES (:travel_id, :accommodation_id)"),
                            {"travel_id": t_e[0], "accommodation_id": t_e[1]}
                )
        await session.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                        ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))

        for data in d_routes:
            await session.execute(text("INSERT INTO directory_route (type_transport, departure_city, \
                    arrival_city, distance, price) \
                VALUES (:type_transport, :departure_city, :arrival_city, :distance, :price)"), data)
            
        for data in route:
            await session.execute(
                    text("INSERT INTO route (d_route_id, travel_id, start_time, end_time) \
                        VALUES (:d_route_id, :travel_id, :start_time, :end_time)"),
                            {
                                "d_route_id": data["d_route_id"],
                                "travel_id": data["travel_id"],
                                "start_time": data["start_time"],
                                "end_time": data["end_time"],
                            }
                        )
                    
        yield session  


@pytest.mark.asyncio
async def test_add_new_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    en = [e for e in [await accommodation_repo.get_by_id(1), await accommodation_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(2), await entertainment_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=await user_repo.get_by_id(1),
        accommodations=en,
        entertainments=acc
    )

    new_route = Route(
        route_id=3,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    await repo.add(new_route)

    result = await db_session.execute(text("SELECT * FROM route ORDER BY id DESC LIMIT 1"))
    route = result.fetchone()

    assert route is not None
    assert new_route.d_route is not None
    assert new_route.travels is not None
    assert route[1] == new_route.d_route.d_route_id
    assert route[2] == new_route.travels.travel_id
    assert route[3] == new_route.start_time
    assert route[4] == new_route.end_time

    travel_result = await db_session.execute(text("SELECT status FROM travel WHERE id = :id"), 
        {"id": new_route.travels.travel_id})
    travel = travel_result.fetchone()
    assert travel is not None
    assert travel[0] == new_route.travels.status

    expected_accommodations = [
        e for e in [await accommodation_repo.get_by_id(1), await accommodation_repo.get_by_id(2)] if e is not None]
    travel_accommodations = list(new_route.travels.accommodations)
    assert len(travel_accommodations) == len(expected_accommodations)
    for accommodation in travel_accommodations:
        expected_accommodation = next(
        (e for e in expected_accommodations if e.accommodation_id == accommodation.accommodation_id),
        None
        )
        assert expected_accommodation is not None
        assert accommodation.price == expected_accommodation.price
        assert accommodation.address == expected_accommodation.address
        assert accommodation.name == expected_accommodation.name
        assert accommodation.type == expected_accommodation.type
        assert accommodation.rating == expected_accommodation.rating
        assert accommodation.check_in == expected_accommodation.check_in
        assert accommodation.check_out == expected_accommodation.check_out

    expected_entertainments = [
        a for a in [await entertainment_repo.get_by_id(2), await entertainment_repo.get_by_id(1)] if a is not None]
    travel_entertainments = list(new_route.travels.entertainments)
    assert len(travel_entertainments) == len(expected_entertainments)
    for entertainment in travel_entertainments:
        assert entertainment is not None
        
        expected_entertainment = next(
            (a for a in expected_entertainments if a.entertainment_id == entertainment.entertainment_id),
            None
        )
        
        assert expected_entertainment is not None

        assert entertainment.duration == expected_entertainment.duration
        assert entertainment.address == expected_entertainment.address
        assert entertainment.event_name == expected_entertainment.event_name
        assert entertainment.event_time == expected_entertainment.event_time
    

@pytest.mark.asyncio
async def test_add_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=3987,
        distance=966,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    en = [e for e in [await accommodation_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=1,
        status="В процессе",
        users=await user_repo.get_by_id(1),
        accommodations=en,
        entertainments=acc
    )

    existing_route = Route(
        route_id=1,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 4, 2, 7, 30, 0),
        end_time=datetime(2025, 4, 6, 7, 0, 0)
    )

    await repo.add(existing_route)
    result = await db_session.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    route = result.fetchone()

    assert route is not None
    assert existing_route.d_route is not None 
    assert existing_route.travels is not None
    assert route[1] == existing_route.d_route.d_route_id
    assert route[2] == existing_route.travels.travel_id
    assert route[3] == existing_route.start_time
    assert route[4] == existing_route.end_time

    travel_result = await db_session.execute(text("SELECT status FROM travel WHERE id = :id"), 
                                                {"id": existing_route.travels.travel_id})
    travel = travel_result.fetchone()

    assert travel is not None
    
    assert travel[0] == existing_route.travels.status

    expected_accommodations = await accommodation_repo.get_by_id(2)
    travel_accommodations = existing_route.travels.accommodations[0]
    assert travel_accommodations is not None
    assert expected_accommodations is not None
    assert travel_accommodations.price == expected_accommodations.price
    assert travel_accommodations.address == expected_accommodations.address
    assert travel_accommodations.name == expected_accommodations.name
    assert travel_accommodations.type == expected_accommodations.type
    assert travel_accommodations.rating == expected_accommodations.rating
    assert travel_accommodations.check_in == expected_accommodations.check_in
    assert travel_accommodations.check_out == expected_accommodations.check_out

    expected_entertainments = await entertainment_repo.get_by_id(1)
    travel_entertainments = existing_route.travels.entertainments

    assert travel_entertainments is not None
    assert expected_entertainments is not None
    assert travel_entertainments[0].duration == expected_entertainments.duration
    assert travel_entertainments[0].address == expected_entertainments.address
    assert travel_entertainments[0].event_name == expected_entertainments.event_name
    assert travel_entertainments[0].event_time == expected_entertainments.event_time


@pytest.mark.asyncio
async def test_update_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    
    en = [e for e in [await accommodation_repo.get_by_id(1), await accommodation_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(2), await entertainment_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None
    
    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=await user_repo.get_by_id(1),
        accommodations=en,
        entertainments=acc
    )

    updated_route = Route(
        route_id=1,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    await repo.update(updated_route)
    result = await db_session.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    route = result.fetchone()

    assert route is not None
    assert updated_route.d_route is not None
    assert route[1] == updated_route.d_route.d_route_id
    assert updated_route.travels is not None
    assert route[2] == updated_route.travels.travel_id
    assert route[3] == updated_route.start_time
    assert route[4] == updated_route.end_time

    travel_result = await db_session.execute(text("SELECT status FROM travel WHERE id = :id"), 
                                                {"id": updated_route.travels.travel_id})
    travel = travel_result.fetchone()

    assert travel is not None
    assert travel[0] == updated_route.travels.status

    expected_accommodations = [
            e for e in [await accommodation_repo.get_by_id(1), await accommodation_repo.get_by_id(2)] if e is not None]
    travel_accommodations = list(updated_route.travels.accommodations)
    assert len(travel_accommodations) == len(expected_accommodations)
    for accommodation in travel_accommodations:
        expected_accommodation = next(
        (e for e in expected_accommodations if e.accommodation_id == accommodation.accommodation_id),
            None
        )
        assert expected_accommodation is not None
        assert accommodation.price == expected_accommodation.price
        assert accommodation.address == expected_accommodation.address
        assert accommodation.name == expected_accommodation.name
        assert accommodation.type == expected_accommodation.type
        assert accommodation.rating == expected_accommodation.rating
        assert accommodation.check_in == expected_accommodation.check_in
        assert accommodation.check_out == expected_accommodation.check_out

    expected_entertainments = [
        a for a in [await entertainment_repo.get_by_id(2), await entertainment_repo.get_by_id(1)] if a is not None
    ]
    
    travel_entertainments = list(updated_route.travels.entertainments)
    assert len(travel_entertainments) == len(expected_entertainments)
    for entertainment in travel_entertainments:
        assert entertainment is not None
        expected_entertainment = next(
            (a for a in expected_entertainments if a.entertainment_id == entertainment.entertainment_id),
            None
        )
        
        assert expected_entertainment is not None

        assert entertainment.duration == expected_entertainment.duration
        assert entertainment.address == expected_entertainment.address
        assert entertainment.event_name == expected_entertainment.event_name
        assert entertainment.event_time == expected_entertainment.event_time


@pytest.mark.asyncio
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )

    en = [e for e in [await accommodation_repo.get_by_id(1), await accommodation_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(2), await entertainment_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=await user_repo.get_by_id(1),
        accommodations=en,
        entertainments=acc
    )

    non_existing_route = Route(
        route_id=6,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    await repo.update(non_existing_route)
    
    result = await db_session.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 999})
    route = result.fetchone()
    
    assert route is None 


@pytest.mark.asyncio
async def test_delete_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)

    await repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    repo = result.fetchone()

    assert repo is None


@pytest.mark.asyncio
async def test_delete_not_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)

    await repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    route = result.fetchone()
    
    assert route is None


@pytest.mark.asyncio
async def test_get_by_id_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    route = await repo.get_by_id(1)

    assert route is not None
    assert route.d_route is not None
    assert route.d_route.departure_city is not None
    assert route.d_route.destination_city is not None
    assert route.d_route.departure_city.name == 'Санкт-Петербург'
    assert route.d_route.destination_city.name == 'Калининград'
    assert route.travels is not None
    assert route.travels.status == "В процессе"
    assert route.travels.users is not None
    assert route.travels.users.user_id == 1
    result_accommodation = await db_session.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == 1
    assert travel_accommodation[0][1:] == (1, 2)

    result_entertainment = await db_session.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == 1
    assert travel_entertainment[0][1:] == (1, 1)


@pytest.mark.asyncio
async def test_get_by_id_not_existing_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)
    route = await repo.get_by_id(132)

    assert route is None


@pytest.mark.asyncio
async def test_get_list_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    repo = RouteRepository(db_session, d_repo, travel_repo)

    list_of_routes = await repo.get_list()

    result = await db_session.execute(text("""
        SELECT dr.id, c1.name AS departure_city, c2.name AS arrival_city
        FROM directory_route dr
        JOIN city c1 ON dr.departure_city = c1.city_id
        JOIN city c2 ON dr.arrival_city = c2.city_id
    """))
    route_map = {row[0]: (row[1], row[2]) for row in result.fetchall()}

    result = await db_session.execute(text("""
        SELECT 
            t.id, 
            t.status, 
            u.id
        FROM travel t
        JOIN users u ON t.user_id = u.id
    """))

    travel_map = {row[0]: {"status": row[1], "user_id": row[2]} for row in result.fetchall()}

    for r in list_of_routes:
        assert r.d_route is not None
        assert r.d_route.departure_city is not None
        assert r.d_route.destination_city is not None

        expected_departure, expected_destination = route_map[r.d_route.d_route_id]
        assert r.d_route.departure_city.name == expected_departure
        assert r.d_route.destination_city.name == expected_destination

        assert r.travels is not None
        expected_travel = travel_map[r.travels.travel_id] 
            
        assert r.travels.status == expected_travel["status"]
        assert r.travels.users is not None
        assert r.travels.users.user_id == expected_travel["user_id"]

        related_accommodations = r.travels.accommodations
        expected_accommodations = [te for te in tr_ent if te[0] == r.travels.travel_id]
        assert len(related_accommodations) == len(expected_accommodations)
        for accommodation in related_accommodations:
            expected_accommodation = accommodations_data[1] if r.travels.travel_id == 1 else accommodations_data[0]

            assert accommodation.price == expected_accommodation["price"]
            assert accommodation.address == expected_accommodation["address"]
            assert accommodation.name == expected_accommodation["name"]
            assert accommodation.type == expected_accommodation["type"]
            assert accommodation.rating == expected_accommodation["rating"]
            assert accommodation.check_in == expected_accommodation["check_in"]
            assert accommodation.check_out == expected_accommodation["check_out"]

        related_entertainments = r.travels.entertainments
        expected_entertainments = [ta for ta in tr_a if ta[0] == r.travels.travel_id]
        assert len(related_entertainments) == len(expected_entertainments)

        for entertainment in related_entertainments:
            assert entertainment is not None, "Entertainment is None"
            expected_entertainment = entertainment_data[0] if r.travels.travel_id == 1 else entertainment_data[1]

            assert entertainment.duration == expected_entertainment["duration"]
            assert entertainment.address == expected_entertainment["address"]
            assert entertainment.event_name == expected_entertainment["event_name"]
            assert entertainment.event_time == expected_entertainment["event_time"]

@pytest.mark.asyncio
async def test_get_routes_by_travel_id_ordered(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    route_repo = RouteRepository(db_session, d_repo, travel_repo)
    result = await route_repo.get_routes_by_travel_id_ordered(1)

    assert len(result) == 2
    assert result[0].start_time < result[1].start_time

@pytest.mark.asyncio
async def test_insert_city_into_route(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    route_repo = RouteRepository(db_session, d_repo, travel_repo)

    initial_routes = await route_repo.get_routes_by_travel_id_ordered(1)
    assert len(initial_routes) == 2
    old_route_ids = [r.route_id for r in initial_routes]
    print("initial_routes: ")
    for route in initial_routes:
        print(f"Route: {route.route_id}, {route.d_route.departure_city.city_id} -> {route.d_route.destination_city.city_id}")


    new_city_id = 1
    await route_repo.insert_city_between(travel_id=1, new_city_id=new_city_id, from_city_id = 3, to_city_id = 5)

    updated_routes = await route_repo.get_routes_by_travel_id_ordered(1)
    print("updated_routes: ")
    for route in updated_routes:
        print(f"Route: {route.route_id}, {route.d_route.departure_city.city_id} -> {route.d_route.destination_city.city_id}")

    assert len(updated_routes) == 3

    updated_route_ids = [r.route_id for r in updated_routes]
    assert any(rid not in updated_route_ids for rid in old_route_ids)

    cities_chain = [r.d_route.departure_city.city_id for r in updated_routes]
    cities_chain.append(updated_routes[-1].d_route.destination_city.city_id)
    assert new_city_id in cities_chain

@pytest.mark.asyncio
async def test_delete_city_from_route(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(db_session)
    d_repo = DirectoryRouteRepository(db_session, city_repo)
    route_repo = RouteRepository(db_session, d_repo, travel_repo)

    city_to_delete = await city_repo.get_by_id(1)
    
    assert city_to_delete is not None
    
    routes_before = await route_repo.get_routes_by_city(1)

    await route_repo.delete_city_from_route(1)

    city_after = await city_repo.get_by_id(1)
    assert city_after is None

    routes_after = await route_repo.get_routes_by_city(1)
    assert len(routes_after) == 0
