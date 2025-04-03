from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.ientertainment_repository import IEntertainmentRepository
from models.entertainment import Entertainment


class EntertainmentRepository(IEntertainmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self) -> list[Entertainment]:
        query = text("SELECT * FROM entertainment")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                Entertainment(
                    entertainment_id=row["id"],
                    cost=row["price"],
                    address=row["address"],
                    name=row["name"],
                    e_type=row["type"],
                    rating=row["rating"],
                    entry_datetime=row["check_in"],
                    departure_datetime=row["check_out"])
                
                for row in result
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка размещения: {e}")
            return []

    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        query = text("SELECT * FROM entertainment WHERE id = :entertainment_id")
        try:
            result = await self.session.execute(query, {"entertainment_id": entertainment_id})
            result = result.mappings().first()
            if result:
                return Entertainment(
                    entertainment_id=result["id"],
                    cost=result["price"],
                    address=result["address"],
                    name=result["name"],
                    e_type=result["type"],
                    rating=result["rating"],
                    entry_datetime=result["check_in"],
                    departure_datetime=result["check_out"])
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении размещения по ID {entertainment_id}: {e}")
            return None

    async def add(self, entertainment: Entertainment) -> None:
        query = text("""
            INSERT INTO entertainment (price, address, name, type, rating, check_in, check_out)
            VALUES (:price, :address, :name, :e_type, :rating, :check_in, :check_out)
        """)
        try:
            await self.session.execute(query, {
                "price": entertainment.cost,
                "address": entertainment.address,
                "name": entertainment.name,
                "e_type": entertainment.e_type,
                "rating": entertainment.rating,
                "check_in": entertainment.entry_datetime,
                "check_out": entertainment.departure_datetime
            })
            await self.session.commit()
        except IntegrityError:
            print("Ошибка: такое размещение уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении размещения: {e}")
            await self.session.rollback()

    async def update(self, update_entertainment: Entertainment) -> None:
        query = text("""
            UPDATE entertainment
            SET price = :price,
                address = :address,
                name = :name,
                type = :e_type,
                rating = :rating,
                check_in = :check_in,
                check_out = :check_out
            WHERE id = :entertainment_id
        """)
        try:
            await self.session.execute(query, {
                    "price": update_entertainment.cost,
                    "address": update_entertainment.address,
                    "name": update_entertainment.name,
                    "e_type": update_entertainment.e_type,
                    "rating": update_entertainment.rating,
                    "check_in": update_entertainment.entry_datetime,
                    "check_out": update_entertainment.departure_datetime,
                    "entertainment_id": update_entertainment.entertainment_id
                })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении размещения с ID {update_entertainment.entertainment_id}: {e}")
            
    async def delete(self, entertainment_id: int) -> None:
        query = text("DELETE FROM entertainment WHERE id = :entertainment_id")
        try:
            await self.session.execute(query, {"entertainment_id": entertainment_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении размещения с ID {entertainment_id}: {e}")
    


