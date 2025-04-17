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
        query = text("SELECT * FROM accommodations ORDER BY id")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                Accommodation(
                    accommodation_id=row["id"],
                    price=row["price"],
                    address=row["address"],
                    name=row["name"],
                    type=row["type"],
                    rating=row["rating"],
                    check_in=row["check_in"],
                    check_out=row["check_out"])
                
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
                    price=result["price"],
                    address=result["address"],
                    name=result["name"],
                    type=result["type"],
                    rating=result["rating"],
                    check_in=result["check_in"],
                    check_out=result["check_out"])
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении размещения по ID {accommodation_id}: {e}")
            return None

    async def add(self, accommodation: Accommodation) -> None:
        query = text("""
            INSERT INTO accommodations (price, address, name, type, rating, check_in, check_out)
            VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out)
        """)
        try:
            await self.session.execute(query, {
                "price": accommodation.price,
                "address": accommodation.address,
                "name": accommodation.name,
                "type": accommodation.type,
                "rating": accommodation.rating,
                "check_in": accommodation.check_in,
                "check_out": accommodation.check_out
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
                type = :type,
                rating = :rating,
                check_in = :check_in,
                check_out = :check_out
            WHERE id = :accommodation_id
        """)
        try:
            await self.session.execute(query, {
                    "price": update_accommodation.price,
                    "address": update_accommodation.address,
                    "name": update_accommodation.name,
                    "type": update_accommodation.type,
                    "rating": update_accommodation.rating,
                    "check_in": update_accommodation.check_in,
                    "check_out": update_accommodation.check_out,
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
    


