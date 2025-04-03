from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.icity_repository import ICityRepository
from models.city import City


class CityRepository(ICityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self) -> list[City]:
        query = text("SELECT * FROM city")
        try:
            result = await self.session.execute(query)
            return [
                City(
                    city_id=row["city_id"],
                    name=row["name"]
                )
                for row in result.mappings()
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка городов: {e}")
            return []

    async def get_by_id(self, city_id: int) -> City | None:
        query = text("SELECT * FROM city WHERE city_id = :city_id")
        try:
            result = await self.session.execute(query, {"city_id": city_id})
            result = result.mappings().first()
            return result if result else None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении пользователя по ID {city_id}: {e}")
            return None

    async def add(self, city: City) -> None:
        query = text("""
            INSERT INTO city (name)
            VALUES (:name)
        """)
        try:
            await self.session.execute(query, {"name": city.name})
            await self.session.commit()
        except IntegrityError:
            print(f"Ошибка: город '{city.name}' уже существует в базе данных.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении города: {e}")
            await self.session.rollback()

    async def update(self, update_city: City) -> None:
        query = text("""
            UPDATE city
            SET name = :name
            WHERE city_id = :city_id
        """)
        try:
            await self.session.execute(query, {
                "city_id": update_city.city_id,
                "name": update_city.name
            })
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print(f"Ошибка при обновлении города с ID {update_city.city_id}: {e}")

    async def delete(self, city_id: int) -> None:
        query = text("DELETE FROM city WHERE city_id = :city_id")
        try:
            await self.session.execute(query, {"city_id": city_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении города с ID {city_id}: {e}")



