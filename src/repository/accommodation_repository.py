from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from models.accommodation import Accommodation


class AccommodationRepository(IAccommodationRepository):
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_list(self) -> list[Accommodation]:
        query = text("SELECT * FROM accommodations")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings()
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

    def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        query = text("SELECT * FROM accommodations WHERE id = :accommodation_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"accommodation_id": accommodation_id}).mappings().first()
                if result:
                    return Accommodation(
                        accommodation_id=result["id"],
                        duration=result["duration"],
                        location=result["address"],
                        a_type=result["event_name"],
                        datetime=result["event_time"])
                return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении развлечений по ID {accommodation_id}: {e}")
            return None

    def add(self, accommodation: Accommodation) -> None:
        query = text("""
            INSERT INTO accommodations (duration, address, event_name, event_time)
            VALUES (:duration, :address, :event_name, :event_time)
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "id": accommodation.accommodation_id,
                    "duration": accommodation.duration,
                    "address": accommodation.location,
                    "event_name": accommodation.a_type,
                    "event_time": accommodation.datetime
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении развлечений: {e}")

    def update(self, update_accommodation: Accommodation) -> None:
        query = text("""
            UPDATE accommodations
            SET duration = :duration,
                address = :address,
                event_name = :event_name,
                event_time = :event_time
            WHERE id = :accommodation_id
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "accommodation_id": update_accommodation.accommodation_id,
                    "duration": update_accommodation.duration,
                    "address": update_accommodation.location,
                    "event_name": update_accommodation.a_type,
                    "event_time": update_accommodation.datetime
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении развлечений с ID {update_accommodation.accommodation_id}: {e}")
            
    def delete(self, accommodation_id: int) -> None:
        query = text("DELETE FROM accommodations WHERE id = :accommodation_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {"accommodation_id": accommodation_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении развлечений с ID {accommodation_id}: {e}")