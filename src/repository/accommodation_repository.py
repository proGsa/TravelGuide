from __future__ import annotations

from sqlalchemy import text
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
                    duration=row["duration"],
                    location=row["address"],
                    a_type=row["event_name"],
                    datetime=row["event_time"]
                )
                for row in result
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка развлечений: {e}")
            return []

    async def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        query = text("SELECT * FROM accommodations WHERE id = :accommodation_id")
        try:
            result = await self.session.execute(query, {"accommodation_id": accommodation_id})
            result = result.mappings().first()
            if result:
                return Accommodation(
                    accommodation_id=result["id"],
                    duration=result["duration"],
                    location=result["address"],
                    a_type=result["event_name"],
                    datetime=result["event_time"])
            return None
            print("Ничего не найдено")
        except SQLAlchemyError as e:
            print(f"Ошибка при получении развлечений по ID {accommodation_id}: {e}")
            return None

    async def add(self, accommodation: Accommodation) -> None:
        query = text("""
            INSERT INTO accommodations (duration, address, event_name, event_time)
            VALUES (:duration, :address, :event_name, :event_time)
        """)
        try:
            await self.session.execute(query, {
                    "id": accommodation.accommodation_id,
                    "duration": accommodation.duration,
                    "address": accommodation.location,
                    "event_name": accommodation.a_type,
                    "event_time": accommodation.datetime
                })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении развлечений: {e}")
            await self.session.rollback()

    async def update(self, update_accommodation: Accommodation) -> None:
        query = text("""
            UPDATE accommodations
            SET duration = :duration,
                address = :address,
                event_name = :event_name,
                event_time = :event_time
            WHERE id = :accommodation_id
        """)
        try:
            await self.session.execute(query, {
                    "accommodation_id": update_accommodation.accommodation_id,
                    "duration": update_accommodation.duration,
                    "address": update_accommodation.location,
                    "event_name": update_accommodation.a_type,
                    "event_time": update_accommodation.datetime
                })
            
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении развлечений с ID {update_accommodation.accommodation_id}: {e}")
            
    async def delete(self, accommodation_id: int) -> None:
        query = text("DELETE FROM accommodations WHERE id = :accommodation_id")
        try:
            await self.session.execute(query, {"accommodation_id": accommodation_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении развлечений с ID {accommodation_id}: {e}")