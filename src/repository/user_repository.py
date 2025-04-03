from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.iuser_repository import IUserRepository
from models.user import User


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        query = text("""
            INSERT INTO users (full_name, passport, phone, email, username, password)
            VALUES (:full_name, :passport, :phone, :email, :username, :password)
        """)
        try:
            await self.session.execute(query, {
                "full_name": user.fio,
                "passport": user.number_passport,
                "phone": user.phone_number,
                "email": user.email,
                "username": user.login,
                "password": user.password
            })
            await self.session.commit() 
        except IntegrityError:
            print("Ошибка: пользователь с таким паспортом, телефоном или email уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            await self.session.rollback()

    async def get_list(self) -> list[User]:
        query = text("SELECT * FROM users")
        try:
            result = await self.session.execute(query)
            return [
                User(
                    user_id=row["id"],
                    fio=row["full_name"],
                    number_passport=row["passport"],
                    phone_number=row["phone"],
                    email=row["email"],
                    login=row["username"],
                    password=row["password"]
                )
                for row in result.mappings()
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка пользователей: {e}")
            return []

    async def get_by_id(self, user_id: int) -> User | None:
        query = text("SELECT * FROM users WHERE id = :user_id")
        try:
            result = await self.session.execute(query, {"user_id": user_id})
            result = result.mappings().first()
            if result:
                return User(
                    user_id=result["id"],
                    fio=result["full_name"],
                    number_passport=result["passport"],
                    phone_number=result["phone"],
                    email=result["email"],
                    login=result["username"],
                    password=result["password"]
                )
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении пользователя по ID {user_id}: {e}")
            return None

    async def get_by_login(self, login: str) -> User | None:
        query = text("SELECT * FROM users WHERE username = :login")
        try:
            result = await self.session.execute(query, {"login": login})
            row = result.mappings().first() 
            if row:
                return User(
                    user_id=row["id"],
                    fio=row["full_name"],
                    number_passport=row["passport"],
                    phone_number=row["phone"],
                    email=row["email"],
                    login=row["username"],
                    password=row["password"]
                )
            return None 
        except SQLAlchemyError as e:
            print(f"Ошибка при получении пользователя по логину: {e}")
            return None
   
    async def update(self, update_user: User) -> None:
        query = text("""
            UPDATE users
            SET full_name = :fio,
                passport = :number_passport,
                phone = :phone_number,
                email = :email,
                username = :login,
                password = :password
            WHERE id = :user_id
        """)
        try:
            await self.session.execute(query, {
                "id": update_user.user_id,
                "fio": update_user.fio,
                "number_passport": update_user.number_passport,
                "phone_number": update_user.phone_number,
                "email": update_user.email,
                "login": update_user.login,
                "password": update_user.password,
                "user_id": update_user.user_id
            })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении пользователя с ID {update_user.user_id}: {e}")

    async def delete(self, user_id: int) -> None:
        query = text("DELETE FROM users WHERE id = :user_id")
        try:
            await self.session.execute(query, {"user_id": user_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении пользователя с ID {user_id}: {e}")
