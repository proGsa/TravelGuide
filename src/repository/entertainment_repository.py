from __future__ import annotations

from sqlalchemy import text
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

    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        query = text("SELECT * FROM entertainment WHERE id = :entertainment_id")
        try:
            result = await self.session.execute(query, {"entertainment_id": entertainment_id})
            result = result.mappings().first()
            if result:
                return Entertainment(
                    entertainment_id=result["id"],
                    duration=result["duration"],
                    location=result["address"],
                    a_type=result["event_name"],
                    datetime=result["event_time"])
            return None
            print("Ничего не найдено")
        except SQLAlchemyError as e:
            print(f"Ошибка при получении развлечений по ID {entertainment_id}: {e}")
            return None

    async def add(self, entertainment: Entertainment) -> None:
        query = text("""
            INSERT INTO entertainment (duration, address, event_name, event_time)
            VALUES (:duration, :address, :event_name, :event_time)
        """)
        try:
            await self.session.execute(query, {
                    "id": entertainment.entertainment_id,
                    "duration": entertainment.duration,
                    "address": entertainment.location,
                    "event_name": entertainment.a_type,
                    "event_time": entertainment.datetime
                })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении развлечений: {e}")
            await self.session.rollback()

    async def update(self, update_entertainment: Entertainment) -> None:
        query = text("""
            UPDATE entertainment
            SET duration = :duration,
                address = :address,
                event_name = :event_name,
                event_time = :event_time
            WHERE id = :entertainment_id
        """)
        try:
            await self.session.execute(query, {
                    "entertainment_id": update_entertainment.entertainment_id,
                    "duration": update_entertainment.duration,
                    "address": update_entertainment.location,
                    "event_name": update_entertainment.a_type,
                    "event_time": update_entertainment.datetime
                })
            
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении развлечений с ID {update_entertainment.entertainment_id}: {e}")
            
    async def delete(self, entertainment_id: int) -> None:
        query = text("DELETE FROM entertainment WHERE id = :entertainment_id")
        try:
            await self.session.execute(query, {"entertainment_id": entertainment_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении развлечений с ID {entertainment_id}: {e}")