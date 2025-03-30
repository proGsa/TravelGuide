from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.icity_repository import ICityRepository
from models.city import City


class CityRepository(ICityRepository):
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_list(self) -> list[City]:
        query = text("SELECT * FROM city")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
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

    def get_by_id(self, city_id: int) -> City | None:
        query = text("SELECT * FROM city WHERE city_id = :city_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"city_id": city_id}).mappings().first()
                return result if result else None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении пользователя по ID {city_id}: {e}")
            return None

    def add(self, city: City) -> None:
        query = text("""
            INSERT INTO city (name)
            VALUES (:name)
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                "name": city.name
                })
        except IntegrityError:
            print(f"Ошибка: город '{city.name}' уже существует в базе данных.")
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении города: {e}")

    def update(self, update_city: City) -> None:
        query = text("""
            UPDATE city
            SET name = :name
            WHERE city_id = :city_id
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "city_id": update_city.city_id,
                    "name": update_city.name
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении города с ID {update_city.city_id}: {e}")

    def delete(self, city_id: int) -> None:
        query = text("DELETE FROM city WHERE city_id = :city_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {"city_id": city_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении города с ID {city_id}: {e}")



