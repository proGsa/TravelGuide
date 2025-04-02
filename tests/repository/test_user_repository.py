from __future__ import annotations

from typing import Generator

import pytest

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from models.user import User
from repository.user_repository import UserRepository


engine = create_engine("postgresql://nastya@localhost:5432/postgres?options=-c%20search_path=test")
with engine.begin() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS test"))

metadata = MetaData(schema='test')

users = [
    {
        "full_name": "Лобач Анастасия Олеговна",
        "passport": "1111111111",
        "phone": "89261111111",
        "email": "nastya@lobach.info",
        "username": "user1",
        "password": "123!e5T78"
    },
    {
        "full_name": "Иванов Иван Иванович",
        "passport": "2222222222",
        "phone": "89262222222",
        "email": "ivanov@ivanov.com",
        "username": "user2",
        "password": "456!f6R89"
    },
    {
        "full_name": "Петров Петр Петрович",
        "passport": "3333333333",
        "phone": "89263333333",
        "email": "petrov@petrov.com",
        "username": "user3",
        "password": "789!g7T90"
    }
]


@pytest.fixture
def db_connection() -> Generator[Connection]:
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")  # Убираем блокировки
        with connection.begin():
            connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            for user_data in users:
                connection.execute(text("INSERT INTO users (full_name, passport, phone, email, \
                            username, password) \
                VALUES (:full_name, :passport, :phone, :email, :username, :password)"), user_data)
            yield connection  


def test_add_new_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    new_user = User(user_id=4, fio="Семенов Семен Семенович", number_passport="4444444444",
        phone_number="89267753309", email="sem@sss.com",
        login="user4", password="6669!g7T90")

    user_repo.add(new_user)

    result = db_connection.execute(text("SELECT * FROM users ORDER BY id DESC LIMIT 1"))
    user = result.mappings().first() 

    assert result is not None
    assert user["full_name"] == "Семенов Семен Семенович"
    assert user["phone"] == "89267753309"
    assert user["passport"] == "4444444444"
    assert user["username"] == "user4"


def test_add_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    existing_user = User(user_id=1, fio="Лобач Анастасия Олеговна", number_passport="1111111111",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")
    
    user_repo.add(existing_user)
    
    result = db_connection.execute(text("SELECT * FROM users WHERE full_name = :full_name"), 
                                        {"full_name": "Лобач Анастасия Олеговна"})
    user = result.fetchone()

    assert user is not None
    assert user[1] == "Лобач Анастасия Олеговна"


def test_update_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    
    updated_user = User(user_id=1, fio="Лобач Анастасия Олеговна", number_passport="5555555555",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")
    user_repo.update(updated_user)

    result = db_connection.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    user = result.fetchone()

    assert user is not None
    assert user[2] == "5555555555"
   

def test_update_not_existing_id(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    non_existing_user = User(user_id=221, fio="Лобач Анастасия Олеговна", number_passport="5555555555",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")

    user_repo.update(non_existing_user)
    
    result = db_connection.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 221})
    user = result.fetchone()
    
    assert user is None 


def test_delete_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    
    user_repo.delete(3)
    
    result = db_connection.execute(text("SELECT * FROM users"))
    user = result.fetchall()

    assert 'user3' not in user


def test_delete_not_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    
    user_repo.delete(999)
    
    result = db_connection.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 999})
    user = result.fetchone()
    
    assert user is None


def test_get_by_id_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    user = user_repo.get_by_id(1)

    assert user is not None
    assert user.fio == "Лобач Анастасия Олеговна"


def test_get_by_id_not_existing_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    user = user_repo.get_by_id(12)

    assert user is None


def test_get_list_user(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    list_of_users = user_repo.get_list()

    list_of_users_simplified = [{"full_name": user.fio, 
                                 "passport": user.number_passport, 
                                 "phone": user.phone_number, 
                                 "email": user.email} for user in list_of_users]

    expected_user_names = [
        {"full_name": "Лобач Анастасия Олеговна", "passport": "1111111111", "phone": "89261111111", 
                                                                    "email": "nastya@lobach.info"},
        {"full_name": "Иванов Иван Иванович", "passport": "2222222222", "phone": "89262222222", 
                                                                    "email": "ivanov@ivanov.com"},
        {"full_name": "Петров Петр Петрович", "passport": "3333333333", "phone": "89263333333", 
                                                                    "email": "petrov@petrov.com"}
    ]

    list_of_users_simplified.sort(key=lambda x: x["full_name"])
    expected_user_names.sort(key=lambda x: x["full_name"])

    assert list_of_users_simplified == expected_user_names

def test_get_exist_user_by_login(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    
    user = user_repo.get_by_login("user1")
    
    assert user is not None
    
    assert user.login == "user1"
    assert user.fio == "Лобач Анастасия Олеговна"
    assert user.email == "nastya@lobach.info"
    assert user.phone_number == "89261111111"
    assert user.number_passport == "1111111111"

def test_get_non_exist_user_by_login(db_connection: Connection) -> None:
    user_repo = UserRepository(db_connection.engine)
    
    user = user_repo.get_by_login("nonexistent_user")
    
    assert user is None
