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

from models.travel import Travel
from models.user import User
from repository.accommodation_repository import AccommodationRepository
from repository.entertainment_repository import EntertainmentRepository
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

EXPECTED_TWO = 2


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
        await session.commit()
        yield session  


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    user = await user_repo.get_by_id(1)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    
    en = [e for e in [await accommodation_repo.get_by_id(2), await accommodation_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(1), await entertainment_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(travel_id=3, status="Завершен", 
        users=user, accommodations=en, entertainments=acc)

    await travel_repo.add(new_travel)

    result = await db_session.execute(text("SELECT * FROM travel ORDER BY id DESC LIMIT 1"))
    travel = result.fetchone()

    assert travel is not None
    assert travel[1] == "Завершен"
    assert user is not None
    assert travel[2] == user.user_id 

    result_accommodation = await db_session.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 3}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == EXPECTED_TWO
    assert travel_accommodation[0][1:] == (3, 2)
    assert travel_accommodation[1][1:] == (3, 1)

    result_entertainment = await db_session.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 3}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == EXPECTED_TWO
    assert travel_entertainment[0][1:] == (3, 1)
    assert travel_entertainment[1][1:] == (3, 2)


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    user = await user_repo.get_by_id(1)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)

    en = [e for e in [await accommodation_repo.get_by_id(2), await accommodation_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(1), await entertainment_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    existing_travel = Travel(travel_id=1, status="В процессе", 
        users=user, accommodations=en, entertainments=acc)

    await travel_repo.add(existing_travel)
    
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), 
                                                                {"id": 1})
    travel = result.fetchone()
    
    assert travel is not None
    assert travel[1] == "В процессе"
    assert user is not None
    assert travel[2] == user.user_id 
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


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    user = await user_repo.get_by_id(1)

    en = [e for e in [await accommodation_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    updated_travel = Travel(travel_id=1, status="В процессе", 
        users=user, accommodations=en, entertainments=acc)

    await travel_repo.update(updated_travel)
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 1})
    travel = result.fetchone()

    assert travel is not None
    assert travel[1] == "В процессе"
    assert user is not None
    assert travel[0] == user.user_id

    result_accommodation = await db_session.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == 1
    assert travel_accommodation[0][2] == 1

    result_entertainment = await db_session.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == 1
    assert travel_entertainment[0][2] == EXPECTED_TWO


@pytest.mark.asyncio(loop_scope="function") 
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    user = User(user_id=4, fio="Семенов Семен Семенович", number_passport="4444444444",
        phone_number="89267753309", email="sem@sss.com",
        login="user4", password="6669!g7T90")
    
    en = [e for e in [await accommodation_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [await entertainment_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    non_existing_travel = Travel(travel_id=999, status="В процессе", 
        users=user, accommodations=en, entertainments=acc)

    await travel_repo.update(non_existing_travel)
    
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    travel = result.fetchone()
    
    assert travel is None 


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    
    await travel_repo.delete(1)
    
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 1})
    travel = result.fetchone()

    assert travel is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_delete_not_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    
    await travel_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    travel = result.fetchone()
    
    assert travel is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    travel = await travel_repo.get_by_id(1)

    assert travel is not None
    assert travel.users is not None
    assert travel.users.user_id == 1
    assert travel.status == "В процессе"


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_by_id_not_existing_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    travel = await travel_repo.get_by_id(132)

    assert travel is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_travel(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    accommodation_repo = AccommodationRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    list_of_travels = await travel_repo.get_list()

    for travel, expected in zip(list_of_travels, travels):
        assert travel.status == expected["status"]
        assert travel.users is not None
        assert travel.users.user_id == expected["user_id"]

        related_accommodations = travel.accommodations 
        assert len(related_accommodations) == len([te for te in tr_ent if te[0] == travel.travel_id])

        for _, accommodation in enumerate(related_accommodations):
            expected_accommodation = accommodations_data[1] if travel.travel_id == 1 else accommodations_data[0]

            assert accommodation.price == expected_accommodation["price"]
            assert accommodation.address == expected_accommodation["address"]
            assert accommodation.name == expected_accommodation["name"]
            assert accommodation.type == expected_accommodation["type"]
            assert accommodation.rating == expected_accommodation["rating"]
            assert accommodation.check_in == expected_accommodation["check_in"]
            assert accommodation.check_out == expected_accommodation["check_out"]

        related_entertainments = travel.entertainments
        assert len(related_entertainments) == len([ta for ta in tr_a if ta[0] == travel.travel_id])

        for _, entertainment in enumerate(related_entertainments):
            assert entertainment is not None, "Entertainment is None"
            expected_entertainment = entertainment_data[0] if travel.travel_id == 1 else entertainment_data[1]

            assert entertainment.duration == expected_entertainment["duration"]
            assert entertainment.address == expected_entertainment["address"]
            assert entertainment.event_name == expected_entertainment["event_name"]
            assert entertainment.event_time == expected_entertainment["event_time"]
