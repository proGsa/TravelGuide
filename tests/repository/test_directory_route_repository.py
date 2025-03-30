from __future__ import annotations

from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.city import City
from models.directory_route import DirectoryRoute
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository


EXPECTED_CITY_ID = 6
EXPECTED_CITY_ID_P = 3
EXPECTED_CITY_ID_K = 5

engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

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


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")  # Убираем блокировки
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE directory_route RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
            connection.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                        ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))
            for data in d_routes:
                connection.execute(text("INSERT INTO directory_route (type_transport, departure_city, \
                    arrival_city, distance, price) \
                VALUES (:type_transport, :departure_city, :arrival_city, :distance, :price)"), data)
            yield connection  


def test_add_new_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    new_city = City(city_id=6, name="Новгород")
    city_repo.add(new_city)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    new_city_from_db = city_repo.get_by_id(6)
    assert new_city_from_db is not None

    departure_city = city_repo.get_by_id(1)
    new_directory_route = DirectoryRoute(d_route_id=13, type_transport="Поезд", departure_city=departure_city, 
                                            destination_city=new_city_from_db, distance=445, cost=1234)
    directory_route_repo.add(new_directory_route)

    result = db_connection.execute(text("SELECT * FROM directory_route ORDER BY id DESC LIMIT 1"))
    directory_route = result.fetchone()

    assert directory_route is not None
    assert directory_route[2] == 1
    assert directory_route[3] == EXPECTED_CITY_ID


def test_add_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    existing_directory_route = DirectoryRoute(d_route_id=1, type_transport="Паром", 
        departure_city=city_repo.get_by_id(3), destination_city=city_repo.get_by_id(5), distance=966, cost=3987)
    
    directory_route_repo.add(existing_directory_route)
    
    result = db_connection.execute(text("SELECT * FROM directory_route WHERE id = :id"), 
                                                                {"id": 1})
    directory_route = result.fetchone()
    
    assert directory_route is not None
    assert directory_route[1] == 'Паром'


def test_update_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    
    updated_directory_route = DirectoryRoute(d_route_id=1, type_transport="Паром", 
        departure_city=city_repo.get_by_id(3), destination_city=city_repo.get_by_id(5), distance=966, cost=3987)
    directory_route_repo.update(updated_directory_route)

    result = db_connection.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 1})
    directory_route = result.fetchone()

    assert directory_route is not None
    assert directory_route[1] == "Паром"
    assert directory_route.id == 1
    assert directory_route[2] == EXPECTED_CITY_ID_P
    assert directory_route[3] == EXPECTED_CITY_ID_K
   

def test_update_not_existing_id(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    non_existing_directory_route = DirectoryRoute(d_route_id=999, type_transport="Паром", 
        departure_city=city_repo.get_by_id(3), destination_city=city_repo.get_by_id(5), distance=966, cost=3987)

    directory_route_repo.update(non_existing_directory_route)
    
    result = db_connection.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 999})
    directory_route = result.fetchone()
    
    assert directory_route is None 


def test_delete_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    
    directory_route_repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 1})
    directory_route = result.fetchone()

    assert directory_route is None


def test_delete_not_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    
    directory_route_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM directory_route WHERE id = :id"), {"id": 999})
    directory_route = result.fetchone()
    
    assert directory_route is None


def test_get_by_id_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    directory_route = directory_route_repo.get_by_id(1)

    assert directory_route is not None
    assert directory_route.d_route_id == 1
    assert directory_route.departure_city is not None
    assert directory_route.destination_city is not None
    assert directory_route.departure_city.city_id == EXPECTED_CITY_ID_P
    assert directory_route.destination_city.city_id == EXPECTED_CITY_ID_K


def test_get_by_id_not_existing_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    directory_route = directory_route_repo.get_by_id(132)

    assert directory_route is None


def test_get_list_directory_route(db_connection: Connection) -> None:
    city_repo = CityRepository(db_connection.engine)
    directory_route_repo = DirectoryRouteRepository(db_connection.engine, city_repo)
    list_of_d_route = directory_route_repo.get_list()

    for route, expected in zip(list_of_d_route, d_routes):
        assert route.type_transport == expected["type_transport"]
        assert route.departure_city is not None
        assert route.destination_city is not None
        assert route.departure_city.city_id == expected["departure_city"]
        assert route.destination_city.city_id == expected["arrival_city"]
        assert route.distance == expected["distance"]
        assert route.cost == expected["price"]
