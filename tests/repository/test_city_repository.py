from __future__ import annotations

from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.city import City
from repository.city_repository import CityRepository


engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

metadata = MetaData(schema='test')


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")  # Убираем блокировки
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
            connection.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                        ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))
            yield connection  


def test_add_new_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    new_city = City(city_id=1, name="Рязань")

    city_repo.add(new_city)

    result = db_connection.execute(text("SELECT * FROM city ORDER BY city_id DESC LIMIT 1"))
    city = result.mappings().first() 
    assert city["name"] == "Рязань"


def test_add_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    existing_city = City(city_id=1, name="Москва")  
    
    city_repo.add(existing_city)
    
    result = db_connection.execute(text("SELECT * FROM city WHERE name = :name"), {"name": "Москва"})
    city = result.fetchone()
    
    assert city is not None
    assert city[1] == "Москва"


def test_update_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    
    updated_city = City(city_id=1, name="Адлер")
    city_repo.update(updated_city)

    result = db_connection.execute(text("SELECT name FROM city WHERE city_id = :city_id"), {"city_id": 1})
    city = result.fetchone()

    assert city is not None
    assert city[0] == "Адлер"
   

def test_update_not_existing_id(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    non_existing_city = City(city_id=999, name="Город")
    
    city_repo.update(non_existing_city)
    
    result = db_connection.execute(text("SELECT * FROM city WHERE city_id = :city_id"), {"city_id": 999})
    city = result.fetchone()
    
    assert city is None 


def test_delete_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    
    city_repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM city"))
    city = result.fetchone()

    assert 'Москва' not in city


def test_delete_not_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    
    city_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM city WHERE city_id = :city_id"), {"city_id": 999})
    city = result.fetchone()
    
    assert city is None


def test_get_by_id_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    city = city_repo.get_by_id(1)

    assert city is not None
    assert city.name == "Москва"


def test_get_by_id_not_existing_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    city = city_repo.get_by_id(12)

    assert city is None


def test_get_list_city(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    list_of_cities = city_repo.get_list()

    city_names = [city.name for city in list_of_cities]
    expected_city_names = ["Москва", "Воронеж", "Санкт-Петербург", "Екатеринбург", "Калининград"]
    
    city_names.sort()
    expected_city_names.sort()

    assert city_names == expected_city_names