from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from models.accommodation import Accommodation


class AccommodationRepository(IAccommodationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self) -> list[Accommodation]:
        query = text("SELECT * FROM accommodations")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                Accommodation(
                    accommodation_id=row["id"],
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

    async def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        query = text("SELECT * FROM accommodations WHERE id = :accommodation_id")
        try:
            result = await self.session.execute(query, {"accommodation_id": accommodation_id})
            result = result.mappings().first()
            if result:
                return Accommodation(
                    accommodation_id=result["id"],
                    cost=result["price"],
                    address=result["address"],
                    name=result["name"],
                    e_type=result["type"],
                    rating=result["rating"],
                    entry_datetime=result["check_in"],
                    departure_datetime=result["check_out"])
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении размещения по ID {accommodation_id}: {e}")
            return None

    async def add(self, accommodation: Accommodation) -> None:
        query = text("""
            INSERT INTO accommodations (price, address, name, type, rating, check_in, check_out)
            VALUES (:price, :address, :name, :e_type, :rating, :check_in, :check_out)
        """)
        try:
            await self.session.execute(query, {
                "price": accommodation.cost,
                "address": accommodation.address,
                "name": accommodation.name,
                "e_type": accommodation.e_type,
                "rating": accommodation.rating,
                "check_in": accommodation.entry_datetime,
                "check_out": accommodation.departure_datetime
            })
            await self.session.commit()
        except IntegrityError:
            print("Ошибка: такое размещение уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении размещения: {e}")
            await self.session.rollback()

    async def update(self, update_accommodation: Accommodation) -> None:
        query = text("""
            UPDATE accommodations
            SET price = :price,
                address = :address,
                name = :name,
                type = :e_type,
                rating = :rating,
                check_in = :check_in,
                check_out = :check_out
            WHERE id = :accommodation_id
        """)
        try:
            await self.session.execute(query, {
                    "price": update_accommodation.cost,
                    "address": update_accommodation.address,
                    "name": update_accommodation.name,
                    "e_type": update_accommodation.e_type,
                    "rating": update_accommodation.rating,
                    "check_in": update_accommodation.entry_datetime,
                    "check_out": update_accommodation.departure_datetime,
                    "accommodation_id": update_accommodation.accommodation_id
                })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении размещения с ID {update_accommodation.accommodation_id}: {e}")
            
    async def delete(self, accommodation_id: int) -> None:
        query = text("DELETE FROM accommodations WHERE id = :accommodation_id")
        try:
            await self.session.execute(query, {"accommodation_id": accommodation_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении размещения с ID {accommodation_id}: {e}")
    


