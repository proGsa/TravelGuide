from __future__ import annotations

from datetime import datetime
from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.entertainment import Entertainment
from repository.entertainment_repository import EntertainmentRepository


engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

metadata = MetaData(schema='test')

entertainment_data = [
        {"price": 46840, "address": "Улица Гоголя, 12", "name": "Four Seasons", "type": "Отель", "rating": 5, 
                "check_in": datetime(2025, 3, 29, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)},
        {"price": 7340, "address": "Улица Толстого, 134", "name": "Мир", "type": "Хостел", "rating": 4, 
                "check_in": datetime(2025, 4, 2, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0)}
    ]


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")  # Убираем блокировки
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE entertainment RESTART IDENTITY CASCADE"))
            for data in entertainment_data:
                connection.execute(text("INSERT INTO entertainment (price, address, name, type, rating, check_in, \
                 check_out) VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out)"), data)
            yield connection  


def test_add_new_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    new_entertainment = Entertainment(entertainment_id=3, cost=33450, address="ул. Дмитриевского, 7",
            name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                                departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    entertainment_repo.add(new_entertainment)

    result = db_connection.execute(text("SELECT * FROM entertainment ORDER BY id DESC LIMIT 1"))
    entertainment = result.mappings().first() 
    assert entertainment["name"] == "ABC"


def test_add_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    existing_entertainment = Entertainment(entertainment_id=3, cost=46840, address="Улица Гоголя", name="Four Seasons", 
                            e_type="Отель", rating=5, entry_datetime=datetime(2025, 3, 29, 12, 30, 0), 
                                    departure_datetime=datetime(2025, 4, 5, 18, 0, 0))

    entertainment_repo.add(existing_entertainment)
    
    result = db_connection.execute(text("SELECT * FROM entertainment WHERE type = :type"), 
                                                                {"type": "Отель"})
    entertainment = result.fetchone()
    
    assert entertainment is not None
    assert entertainment[4] == "Отель"


def test_update_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    
    updated_entertainment = Entertainment(entertainment_id=1, cost=33450, address="ул. Дмитриевского, 7", 
                name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                            departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    entertainment_repo.update(updated_entertainment)

    result = db_connection.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 1})
    entertainment = result.fetchone()

    assert entertainment is not None
    assert entertainment[3] == "ABC"
   

def test_update_not_existing_id(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    non_existing_entertainment = Entertainment(entertainment_id=3, cost=33450, address="ул. Дмитриевского, 7", 
                    name="ABC", e_type="Квартира", rating=3, entry_datetime=datetime(2025, 4, 2, 14, 0, 0), 
                                                departure_datetime=datetime(2025, 4, 6, 18, 0, 0))

    entertainment_repo.update(non_existing_entertainment)
    
    result = db_connection.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 999})
    entertainment = result.fetchone()
    
    assert entertainment is None 


def test_delete_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    
    entertainment_repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM entertainment"))
    entertainment = result.fetchone()

    assert 'Four Seasons' not in entertainment


def test_delete_not_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    
    entertainment_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM entertainment WHERE id = :id"), {"id": 999})
    entertainment = result.fetchone()
    
    assert entertainment is None


def test_get_by_id_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    entertainment = entertainment_repo.get_by_id(1)

    assert entertainment is not None
    assert entertainment.name == "Four Seasons"


def test_get_by_id_not_existing_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    entertainment = entertainment_repo.get_by_id(12)

    assert entertainment is None


def test_get_list_entertainment(db_connection: Connection) -> None:
    entertainment_repo = EntertainmentRepository(db_connection.engine)
    list_of_entertainment = entertainment_repo.get_list()

    entertainment_names = [entertainment.e_type for entertainment in list_of_entertainment]
    expected_entertainment_names = [entertainment["type"] for entertainment in entertainment_data]
    
    entertainment_names.sort()
    expected_entertainment_names.sort()

    assert entertainment_names == expected_entertainment_names