from __future__ import annotations

from datetime import datetime
from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.accommodation import Accommodation
from repository.accommodation_repository import AccommodationRepository


engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

metadata = MetaData(schema='test')

accommodations_data = [
        {"duration": "4 часа", "address": "Главная площадь", "event_name": "Концерт", 
                                            "event_time": datetime(2025, 4, 10, 16, 0, 0)},
        {"duration": "3 часа", "address": "ул. Кузнецова, 4", "event_name": "Выставка", 
                                            "event_time": datetime(2025, 4, 5, 10, 0, 0)}
    ]


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")  # Убираем блокировки
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE accommodations RESTART IDENTITY CASCADE"))
            for data in accommodations_data:
                connection.execute(text("INSERT INTO accommodations (duration, address, event_name, event_time) \
                VALUES (:duration, :address, :event_name, :event_time)"), data)
            yield connection  


def test_add_new_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    new_accommodation = Accommodation(accommodation_id=3, duration="2 часа", location="Красная площадь", 
                                            a_type="Музей", datetime=datetime(2025, 4, 2, 14, 0, 0))

    accommodation_repo.add(new_accommodation)

    result = db_connection.execute(text("SELECT * FROM accommodations ORDER BY id DESC LIMIT 1"))
    accommodation = result.mappings().first() 
    assert accommodation["address"] == "Красная площадь"


def test_add_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    existing_accommodation = Accommodation(accommodation_id=1, duration="4 часа", location="Главная площадь",
                                            a_type="Концерт", datetime=datetime(2025, 4, 10, 16, 0, 0))
    
    accommodation_repo.add(existing_accommodation)
    
    result = db_connection.execute(text("SELECT * FROM accommodations WHERE duration = :duration"), 
                                                                {"duration": "4 часа"})
    accommodation = result.fetchone()
    
    assert accommodation is not None
    assert accommodation[2] == "Главная площадь"


def test_update_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    
    updated_accommodation = Accommodation(accommodation_id=1, duration="2 часа", location="Главная площадь",
                                            a_type="Фестиваль", datetime=datetime(2025, 4, 2, 14, 0, 0))
    accommodation_repo.update(updated_accommodation)

    result = db_connection.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 1})
    accommodation = result.fetchone()

    assert accommodation is not None
    assert accommodation[1] == "2 часа"
   

def test_update_not_existing_id(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    non_existing_accommodation = Accommodation(accommodation_id=999, duration="2 часа", location="Главная площадь", 
                                                a_type="Фестиваль", datetime=datetime(2025, 4, 2, 14, 0, 0))
    
    accommodation_repo.update(non_existing_accommodation)
    
    result = db_connection.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 999})
    accommodation = result.fetchone()
    
    assert accommodation is None 


def test_delete_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    
    accommodation_repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM accommodations"))
    accommodation = result.fetchone()

    assert '4 часа' not in accommodation


def test_delete_not_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    
    accommodation_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM accommodations WHERE id = :id"), {"id": 999})
    accommodation = result.fetchone()
    
    assert accommodation is None


def test_get_by_id_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    accommodation = accommodation_repo.get_by_id(1)

    assert accommodation is not None
    assert accommodation.a_type == "Концерт"


def test_get_by_id_not_existing_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    accommodation = accommodation_repo.get_by_id(12)

    assert accommodation is None


def test_get_list_accommodation(db_connection: Connection) -> None:
    accommodation_repo = AccommodationRepository(db_connection.engine)
    list_of_accommodations = accommodation_repo.get_list()

    accommodation_names = [accommodations.a_type for accommodations in list_of_accommodations]
    expected_accommodation_names = [accommodation["event_name"] for accommodation in accommodations_data]
    
    accommodation_names.sort()
    expected_accommodation_names.sort()

    assert accommodation_names == expected_accommodation_names