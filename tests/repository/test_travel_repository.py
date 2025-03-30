from __future__ import annotations

from datetime import datetime
from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.travel import Travel
from models.user import User
from repository.accommodation_repository import AccommodationRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.travel_repository import TravelRepository
from repository.user_repository import UserRepository


engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

metadata = MetaData(schema='test')

travels = [{"status": "В процессе", "user_id": 1}, {"status": "Завершен", "user_id": 1}]

entertainment_data = [
        {"price": 46840, "address": "Улица Гоголя, 12", "name": "Four Seasons", "type": "Отель", "rating": 5, 
                "check_in": datetime(2025, 3, 29, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)},
        {"price": 7340, "address": "Улица Толстого, 134", "name": "Мир", "type": "Хостел", "rating": 4, 
                "check_in": datetime(2025, 4, 2, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)}
    ]
accommodations_data = [
        {"duration": "4 часа", "address": "Главная площадь", "event_name": "Концерт", 
                                            "event_time": datetime(2025, 4, 10, 16, 0, 0)},
        {"duration": "3 часа", "address": "ул. Кузнецова, 4", "event_name": "Выставка", 
                                            "event_time": datetime(2025, 4, 5, 10, 0, 0)}
    ]

tr_ent = [(1, 2), (2, 1)]

tr_a = [(1, 1), (2, 2)]

EXPECTED_TWO = 2


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE travel_entertainment RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE travel_accommodations RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE entertainment RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE accommodations RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE travel RESTART IDENTITY CASCADE"))

            connection.execute(text("""
                INSERT INTO users (full_name, passport, phone, email, username, password)
                VALUES 
                ('Лобач Анастасия Олеговна', '1111111111', '89261111111', 'nastya@lobach.info', 'user1', '123!e5T78')
            """))

            for data in entertainment_data:
                connection.execute(text("INSERT INTO entertainment (price, address, name, type, rating, check_in, \
                 check_out) VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out)"), data)
            for data in accommodations_data:
                connection.execute(text("INSERT INTO accommodations (duration, address, event_name, event_time) \
                VALUES (:duration, :address, :event_name, :event_time)"), data)
            for data in travels:
                connection.execute(text("INSERT INTO travel (status, user_id) \
                VALUES (:status, :user_id)"), data)
            for t_a in tr_a:
                connection.execute(
                    text("INSERT INTO travel_accommodations (travel_id, accommodation_id) \
                        VALUES (:travel_id, :accommodation_id)"), 
                        {
                            "travel_id": t_a[0],
                            "accommodation_id": t_a[1]
                        }
                )
            for t_e in tr_ent:
                connection.execute(
                    text("INSERT INTO travel_entertainment (travel_id, entertainment_id) \
                        VALUES (:travel_id, :entertainment_id)"),
                            {"travel_id": t_e[0], "entertainment_id": t_e[1]}
                )
            
            yield connection  


def test_add_new_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    user = user_repo.get_by_id(1)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    
    en = [e for e in [entertainment_repo.get_by_id(2), entertainment_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(1), accommodation_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(travel_id=3, status="Завершен", 
        users=user, entertainments=en, accommodations=acc)

    travel_repo.add(new_travel)

    result = db_connection.execute(text("SELECT * FROM travel ORDER BY id DESC LIMIT 1"))
    travel = result.fetchone()

    assert travel is not None
    assert travel[1] == "Завершен"
    assert user is not None
    assert travel[2] == user.user_id 

    result_entertainment = db_connection.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 3}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == EXPECTED_TWO
    assert travel_entertainment[0][1:] == (3, 2)
    assert travel_entertainment[1][1:] == (3, 1)

    result_accommodation = db_connection.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 3}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == EXPECTED_TWO
    assert travel_accommodation[0][1:] == (3, 1)
    assert travel_accommodation[1][1:] == (3, 2)


def test_add_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    user = user_repo.get_by_id(1)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)

    en = [e for e in [entertainment_repo.get_by_id(2), entertainment_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(1), accommodation_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    existing_travel = Travel(travel_id=1, status="В процессе", 
        users=user, entertainments=en, accommodations=acc)

    travel_repo.add(existing_travel)
    
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), 
                                                                {"id": 1})
    travel = result.fetchone()
    
    assert travel is not None
    assert travel[1] == "В процессе"
    assert user is not None
    assert travel[2] == user.user_id 
    result_entertainment = db_connection.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == 1
    assert travel_entertainment[0][1:] == (1, 2)

    result_accommodation = db_connection.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == 1
    assert travel_accommodation[0][1:] == (1, 1)


def test_update_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    user = user_repo.get_by_id(1)

    en = [e for e in [entertainment_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    updated_travel = Travel(travel_id=1, status="B обработке", 
        users=user, entertainments=en, accommodations=acc)

    travel_repo.update(updated_travel)
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 1})
    travel = result.fetchone()

    assert travel is not None
    assert travel[1] == "B обработке"
    assert user is not None
    assert travel[0] == user.user_id

    result_entertainment = db_connection.execute(
        text("SELECT * FROM travel_entertainment WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_entertainment = result_entertainment.fetchall()
    assert len(travel_entertainment) == 1
    assert travel_entertainment[0][2] == 1

    result_accommodation = db_connection.execute(
        text("SELECT * FROM travel_accommodations WHERE travel_id = :travel_id"), {"travel_id": 1}
    )
    travel_accommodation = result_accommodation.fetchall()
    assert len(travel_accommodation) == 1
    assert travel_accommodation[0][2] == EXPECTED_TWO


def test_update_not_existing_id(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    user = User(user_id=4, fio="Семенов Семен Семенович", number_passport="4444444444",
        phone_number="89267753309", email="sem@sss.com",
        login="user4", password="6669!g7T90")
    
    en = [e for e in [entertainment_repo.get_by_id(1)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(2)] if a is not None]

    assert acc is not None
    assert en is not None

    non_existing_travel = Travel(travel_id=999, status="B обработке", 
        users=user, entertainments=en, accommodations=acc)

    travel_repo.update(non_existing_travel)
    
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    travel = result.fetchone()
    
    assert travel is None 


def test_delete_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    
    travel_repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 1})
    travel = result.fetchone()

    assert travel is None


def test_delete_not_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    
    travel_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    travel = result.fetchone()
    
    assert travel is None


def test_get_by_id_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    travel = travel_repo.get_by_id(1)

    assert travel is not None
    assert travel.users is not None
    assert travel.users.user_id == 1
    assert travel.status == "В процессе"


def test_get_by_id_not_existing_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    travel = travel_repo.get_by_id(132)

    assert travel is None


def test_get_list_travel(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    list_of_travels = travel_repo.get_list()

    for travel, expected in zip(list_of_travels, travels):
        assert travel.status == expected["status"]
        assert travel.users is not None
        assert travel.users.user_id == expected["user_id"]

        related_entertainments = travel.entertainments 
        assert len(related_entertainments) == len([te for te in tr_ent if te[0] == travel.travel_id])

        for _, entertainment in enumerate(related_entertainments):
            expected_entertainment = entertainment_data[1] if travel.travel_id == 1 else entertainment_data[0]

            assert entertainment.cost == expected_entertainment["price"]
            assert entertainment.address == expected_entertainment["address"]
            assert entertainment.name == expected_entertainment["name"]
            assert entertainment.e_type == expected_entertainment["type"]
            assert entertainment.rating == expected_entertainment["rating"]
            assert entertainment.entry_datetime == expected_entertainment["check_in"]
            assert entertainment.departure_datetime == expected_entertainment["check_out"]

        related_accommodations = travel.accommodations
        assert len(related_accommodations) == len([ta for ta in tr_a if ta[0] == travel.travel_id])

        for _, accommodation in enumerate(related_accommodations):
            assert accommodation is not None, "Accommodation is None"  # проверка на None
            expected_accommodation = accommodations_data[0] if travel.travel_id == 1 else accommodations_data[1]

            assert accommodation.duration == expected_accommodation["duration"]
            assert accommodation.location == expected_accommodation["address"]
            assert accommodation.a_type == expected_accommodation["event_name"]
            assert accommodation.datetime == expected_accommodation["event_time"]