from __future__ import annotations

from datetime import datetime
from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
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

route = [
    {"d_route_id": 1, "travel_id": 1, "start_time": datetime(2025, 4, 2, 7, 30, 0),
                                     "end_time": datetime(2025, 4, 6, 7, 0, 0)}, 
    {"d_route_id": 11, "travel_id": 2, "start_time": datetime(2025, 3, 29, 6, 50, 0), 
                                        "end_time": datetime(2025, 4, 5, 22, 45, 0)}
]


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

            connection.execute(text("TRUNCATE TABLE city RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE directory_route RESTART IDENTITY CASCADE"))
            connection.execute(text("TRUNCATE TABLE route RESTART IDENTITY CASCADE"))

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
            connection.execute(text("INSERT INTO city (name) VALUES ('Москва'), \
                        ('Воронеж'), ('Санкт-Петербург'), ('Екатеринбург'), ('Калининград')"))

            for data in d_routes:
                connection.execute(text("INSERT INTO directory_route (type_transport, departure_city, \
                    arrival_city, distance, price) \
                VALUES (:type_transport, :departure_city, :arrival_city, :distance, :price)"), data)
            
            for data in route:
                connection.execute(
                    text("INSERT INTO route (d_route_id, travel_id, start_time, end_time) \
                        VALUES (:d_route_id, :travel_id, :start_time, :end_time)"),
                            {
                                "d_route_id": data["d_route_id"],
                                "travel_id": data["travel_id"],
                                "start_time": data["start_time"],
                                "end_time": data["end_time"],
                            }
                        )
                    
            yield connection  


def test_add_new_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    en = [e for e in [entertainment_repo.get_by_id(1), entertainment_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(2), accommodation_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=user_repo.get_by_id(1),
        entertainments=en,
        accommodations=acc
    )

    new_route = Route(
        route_id=3,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    repo.add(new_route)

    result = db_connection.execute(text("SELECT * FROM route ORDER BY id DESC LIMIT 1"))
    route = result.fetchone()

    assert route is not None
    assert new_route.d_route is not None
    assert new_route.travels is not None
    assert route[1] == new_route.d_route.d_route_id
    assert route[2] == new_route.travels.travel_id
    assert route[3] == new_route.start_time
    assert route[4] == new_route.end_time

    travel_result = db_connection.execute(text("SELECT status FROM travel WHERE id = :id"), 
        {"id": new_route.travels.travel_id})
    travel = travel_result.fetchone()
    assert travel is not None
    assert travel[0] == new_route.travels.status

    expected_entertainments = [
        e for e in [entertainment_repo.get_by_id(1), entertainment_repo.get_by_id(2)] if e is not None]
    travel_entertainments = list(new_route.travels.entertainments)
    assert len(travel_entertainments) == len(expected_entertainments)
    for entertainment in travel_entertainments:
        expected_entertainment = next(
        (e for e in expected_entertainments if e.entertainment_id == entertainment.entertainment_id),
        None
        )
        assert expected_entertainment is not None
        assert entertainment.cost == expected_entertainment.cost
        assert entertainment.address == expected_entertainment.address
        assert entertainment.name == expected_entertainment.name
        assert entertainment.e_type == expected_entertainment.e_type
        assert entertainment.rating == expected_entertainment.rating
        assert entertainment.entry_datetime == expected_entertainment.entry_datetime
        assert entertainment.departure_datetime == expected_entertainment.departure_datetime

    expected_accommodations = [
        a for a in [accommodation_repo.get_by_id(2), accommodation_repo.get_by_id(1)] if a is not None]
    travel_accommodations = list(new_route.travels.accommodations)
    assert len(travel_accommodations) == len(expected_accommodations)
    for accommodation in travel_accommodations:
        assert accommodation is not None
        
        expected_accommodation = next(
            (a for a in expected_accommodations if a.accommodation_id == accommodation.accommodation_id),
            None
        )
        
        assert expected_accommodation is not None

        assert accommodation.duration == expected_accommodation.duration
        assert accommodation.location == expected_accommodation.location
        assert accommodation.a_type == expected_accommodation.a_type
        assert accommodation.datetime == expected_accommodation.datetime
    

def test_add_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=3987,
        distance=966,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    en = [e for e in [entertainment_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=1,
        status="В процессе",
        users=user_repo.get_by_id(1),
        entertainments=en,
        accommodations=acc
    )

    existing_route = Route(
        route_id=1,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 4, 2, 7, 30, 0),
        end_time=datetime(2025, 4, 6, 7, 0, 0)
    )

    repo.add(existing_route)
    result = db_connection.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    route = result.fetchone()

    assert route is not None
    assert existing_route.d_route is not None 
    assert existing_route.travels is not None
    assert route[1] == existing_route.d_route.d_route_id
    assert route[2] == existing_route.travels.travel_id
    assert route[3] == existing_route.start_time
    assert route[4] == existing_route.end_time

    travel_result = db_connection.execute(text("SELECT status FROM travel WHERE id = :id"), 
                                                {"id": existing_route.travels.travel_id})
    travel = travel_result.fetchone()

    assert travel is not None
    
    assert travel[0] == existing_route.travels.status

    expected_entertainments = entertainment_repo.get_by_id(2)
    travel_entertainments = existing_route.travels.entertainments[0]
    assert travel_entertainments is not None
    assert expected_entertainments is not None
    assert travel_entertainments.cost == expected_entertainments.cost
    assert travel_entertainments.address == expected_entertainments.address
    assert travel_entertainments.name == expected_entertainments.name
    assert travel_entertainments.e_type == expected_entertainments.e_type
    assert travel_entertainments.rating == expected_entertainments.rating
    assert travel_entertainments.entry_datetime == expected_entertainments.entry_datetime
    assert travel_entertainments.departure_datetime == expected_entertainments.departure_datetime

    expected_accommodations = accommodation_repo.get_by_id(1)
    travel_accommodations = existing_route.travels.accommodations

    assert travel_accommodations is not None
    assert expected_accommodations is not None
    assert travel_accommodations[0].duration == expected_accommodations.duration
    assert travel_accommodations[0].location == expected_accommodations.location
    assert travel_accommodations[0].a_type == expected_accommodations.a_type
    assert travel_accommodations[0].datetime == expected_accommodations.datetime


def test_update_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )
    
    en = [e for e in [entertainment_repo.get_by_id(1), entertainment_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(2), accommodation_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None
    
    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=user_repo.get_by_id(1),
        entertainments=en,
        accommodations=acc
    )

    updated_route = Route(
        route_id=1,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    repo.update(updated_route)
    result = db_connection.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    route = result.fetchone()

    assert route is not None
    assert updated_route.d_route is not None
    assert route[1] == updated_route.d_route.d_route_id
    assert updated_route.travels is not None
    assert route[2] == updated_route.travels.travel_id
    assert route[3] == updated_route.start_time
    assert route[4] == updated_route.end_time

    travel_result = db_connection.execute(text("SELECT status FROM travel WHERE id = :id"), 
                                                {"id": updated_route.travels.travel_id})
    travel = travel_result.fetchone()

    assert travel is not None
    assert travel[0] == updated_route.travels.status

    expected_entertainments = [
            e for e in [entertainment_repo.get_by_id(1), entertainment_repo.get_by_id(2)] if e is not None]
    travel_entertainments = list(updated_route.travels.entertainments)
    assert len(travel_entertainments) == len(expected_entertainments)
    for entertainment in travel_entertainments:
        expected_entertainment = next(
        (e for e in expected_entertainments if e.entertainment_id == entertainment.entertainment_id),
            None
        )
        assert expected_entertainment is not None
        assert entertainment.cost == expected_entertainment.cost
        assert entertainment.address == expected_entertainment.address
        assert entertainment.name == expected_entertainment.name
        assert entertainment.e_type == expected_entertainment.e_type
        assert entertainment.rating == expected_entertainment.rating
        assert entertainment.entry_datetime == expected_entertainment.entry_datetime
        assert entertainment.departure_datetime == expected_entertainment.departure_datetime

    expected_accommodations = [
        a for a in [accommodation_repo.get_by_id(2), accommodation_repo.get_by_id(1)] if a is not None
    ]
    
    travel_accommodations = list(updated_route.travels.accommodations)
    assert len(travel_accommodations) == len(expected_accommodations)
    for accommodation in travel_accommodations:
        assert accommodation is not None
        expected_accommodation = next(
            (a for a in expected_accommodations if a.accommodation_id == accommodation.accommodation_id),
            None
        )
        
        assert expected_accommodation is not None

        assert accommodation.duration == expected_accommodation.duration
        assert accommodation.location == expected_accommodation.location
        assert accommodation.a_type == expected_accommodation.a_type
        assert accommodation.datetime == expected_accommodation.datetime


def test_update_not_existing_id(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    
    d_r = DirectoryRoute(
        d_route_id=1, 
        type_transport="Паром",
        cost=25866,
        distance=300000,
        departure_city=City(city_id=3, name='Санкт-Петербург'),
        destination_city=City(city_id=5, name='Калининград')
    )

    en = [e for e in [entertainment_repo.get_by_id(1), entertainment_repo.get_by_id(2)] if e is not None]
    acc = [a for a in [accommodation_repo.get_by_id(2), accommodation_repo.get_by_id(1)] if a is not None]

    assert acc is not None
    assert en is not None

    new_travel = Travel(
        travel_id=2,
        status="Завершен",
        users=user_repo.get_by_id(1),
        entertainments=en,
        accommodations=acc
    )

    non_existing_route = Route(
        route_id=6,
        d_route=d_r,
        travels=new_travel,
        start_time=datetime(2025, 3, 27, 17, 24, 0),
        end_time=datetime(2025, 4, 13, 10, 0, 0) 
    )

    repo.update(non_existing_route)
    
    result = db_connection.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 999})
    route = result.fetchone()
    
    assert route is None 


def test_delete_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)

    repo.delete(1)
    
    result = db_connection.execute(text("SELECT * FROM route WHERE id = :id"), {"id": 1})
    repo = result.fetchone()

    assert repo is None


def test_delete_not_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)

    repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM travel WHERE id = :id"), {"id": 999})
    route = result.fetchone()
    
    assert route is None


def test_get_by_id_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    route = repo.get_by_id(1)

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


def test_get_by_id_not_existing_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)
    route = repo.get_by_id(132)

    assert route is None


def test_get_list_route(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    entertainment_repo = EntertainmentRepository(engine)
    accommodation_repo = AccommodationRepository(engine)
    travel_repo = TravelRepository(db_connection.engine, user_repo, entertainment_repo, accommodation_repo)
    city_repo = CityRepository(engine)
    d_repo = DirectoryRouteRepository(engine, city_repo)
    repo = RouteRepository(engine, d_repo, travel_repo)

    list_of_routes = repo.get_list()

    result = db_connection.execute(text("""
        SELECT dr.id, c1.name AS departure_city, c2.name AS arrival_city
        FROM directory_route dr
        JOIN city c1 ON dr.departure_city = c1.city_id
        JOIN city c2 ON dr.arrival_city = c2.city_id
    """))
    route_map = {row[0]: (row[1], row[2]) for row in result.fetchall()}

    result = db_connection.execute(text("""
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

        related_entertainments = r.travels.entertainments
        expected_entertainments = [te for te in tr_ent if te[0] == r.travels.travel_id]
        assert len(related_entertainments) == len(expected_entertainments)
        for entertainment in related_entertainments:
            expected_entertainment = entertainment_data[1] if r.travels.travel_id == 1 else entertainment_data[0]

            assert entertainment.cost == expected_entertainment["price"]
            assert entertainment.address == expected_entertainment["address"]
            assert entertainment.name == expected_entertainment["name"]
            assert entertainment.e_type == expected_entertainment["type"]
            assert entertainment.rating == expected_entertainment["rating"]
            assert entertainment.entry_datetime == expected_entertainment["check_in"]
            assert entertainment.departure_datetime == expected_entertainment["check_out"]

        related_accommodations = r.travels.accommodations
        expected_accommodations = [ta for ta in tr_a if ta[0] == r.travels.travel_id]
        assert len(related_accommodations) == len(expected_accommodations)

        for accommodation in related_accommodations:
            assert accommodation is not None, "Accommodation is None"
            expected_accommodation = accommodations_data[0] if r.travels.travel_id == 1 else accommodations_data[1]

            assert accommodation.duration == expected_accommodation["duration"]
            assert accommodation.location == expected_accommodation["address"]
            assert accommodation.a_type == expected_accommodation["event_name"]
            assert accommodation.datetime == expected_accommodation["event_time"]