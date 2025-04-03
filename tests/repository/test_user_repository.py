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

from models.user import User
from repository.user_repository import UserRepository


engine = create_async_engine("postgresql+asyncpg://nastya@localhost:5432/postgres", echo=True)
AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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


@pytest_asyncio.fixture(scope="session")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionMaker() as session:
        await session.execute(text("SET search_path TO test"))
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))

        for user_data in users:
            await session.execute(text("""
                INSERT INTO users (full_name, passport, phone, email, username, password)
                VALUES (:full_name, :passport, :phone, :email, :username, :password)
            """), user_data)
        await session.commit()
        yield session


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_new_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    new_user = User(user_id=4, fio="Семенов Семен Семенович", number_passport="4444444444",
        phone_number="89267753309", email="sem@sss.com",
        login="user4", password="6669!g7T90")

    await user_repo.add(new_user)

    result = await db_session.execute(text("SELECT * FROM users ORDER BY id DESC LIMIT 1"))
    user = result.mappings().first()

    assert result is not None
    assert user["full_name"] == "Семенов Семен Семенович"
    assert user["phone"] == "89267753309"
    assert user["passport"] == "4444444444"
    assert user["username"] == "user4"


@pytest.mark.asyncio(loop_scope="function") 
async def test_add_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    existing_user = User(user_id=1, fio="Лобач Анастасия Олеговна", number_passport="1111111111",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")
    
    try:
        await user_repo.add(existing_user)
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    
    result = await db_session.execute(text("SELECT * FROM users WHERE full_name = :full_name"), 
                                        {"full_name": "Лобач Анастасия Олеговна"})
    user = result.fetchone()

    assert user is not None
    assert user[1] == "Лобач Анастасия Олеговна"
    

@pytest.mark.asyncio
async def test_update_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    
    updated_user = User(user_id=1, fio="Лобач Анастасия Олеговна", number_passport="5555555555",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")
    await user_repo.update(updated_user)

    result = await db_session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    user = result.fetchone()

    assert user is not None
    assert user[2] == "5555555555"
   

@pytest.mark.asyncio
async def test_update_not_existing_id(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    non_existing_user = User(user_id=221, fio="Лобач Анастасия Олеговна", number_passport="5555555555",
        phone_number="89261111111", email="nastya@lobach.info",
        login="user1", password="123!e5T78")

    await user_repo.update(non_existing_user)
    
    result = await db_session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 221})
    user = result.fetchone()
    
    assert user is None 


@pytest.mark.asyncio
async def test_delete_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    
    await user_repo.delete(3)
    
    result = await db_session.execute(text("SELECT username FROM users"))
    users = result.scalars()  # Получаем список всех username
    
    assert "user3" not in users 


@pytest.mark.asyncio
async def test_delete_not_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    
    await user_repo.delete(999)
    
    result = await db_session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 999})
    user = result.fetchone()
    
    assert user is None


@pytest.mark.asyncio
async def test_get_by_id_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id(1)

    assert user is not None
    assert user.fio == "Лобач Анастасия Олеговна"


@pytest.mark.asyncio
async def test_get_by_id_not_existing_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id(12)

    assert user is None


@pytest.mark.asyncio(loop_scope="function") 
async def test_get_list_user(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    list_of_users = await user_repo.get_list()

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


@pytest.mark.asyncio
async def test_get_exist_user_by_login(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    
    user = await user_repo.get_by_login("user1")
    
    assert user is not None
    
    assert user.login == "user1"
    assert user.fio == "Лобач Анастасия Олеговна"
    assert user.email == "nastya@lobach.info"
    assert user.phone_number == "89261111111"
    assert user.number_passport == "1111111111"


@pytest.mark.asyncio
async def test_get_non_exist_user_by_login(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    
    user = await user_repo.get_by_login("nonexistent_user")
    
    assert user is None
