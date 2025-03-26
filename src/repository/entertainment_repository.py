from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.ientertainment_repository import IEntertainmentRepository
from models.entertainment import Entertainment


class EntertainmentRepository(IEntertainmentRepository):
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_list(self) -> list[Entertainment]:
        query = text("SELECT * FROM travel_db.entertainment")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings()
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

    def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        query = text("SELECT * FROM travel_db.entertainment WHERE id = :entertainment_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"entertainment_id": entertainment_id}).mappings().first()
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

    def add(self, entertainment: Entertainment) -> None:
        query = text("""
            INSERT INTO travel_db.entertainment (price, address, name, type, rating, check_in, check_out)
            VALUES (:price, :address, :name, :e_type, :rating, :check_in, :check_out)
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "price": entertainment.cost,
                    "address": entertainment.address,
                    "name": entertainment.name,
                    "e_type": entertainment.e_type,
                    "rating": entertainment.rating,
                    "check_in": entertainment.entry_datetime,
                    "check_out": entertainment.departure_datetime
                })
        except IntegrityError:
            print("Ошибка: такое размещение уже существует.")
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении размещения: {e}")

    def update(self, update_entertainment: Entertainment) -> None:
        query = text("""
            UPDATE travel_db.entertainment
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
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "price": update_entertainment.cost,
                    "address": update_entertainment.address,
                    "name": update_entertainment.name,
                    "e_type": update_entertainment.e_type,
                    "rating": update_entertainment.rating,
                    "check_in": update_entertainment.entry_datetime,
                    "check_out": update_entertainment.departure_datetime,
                    "entertainment_id": update_entertainment.entertainment_id
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении размещения с ID {update_entertainment.entertainment_id}: {e}")
            
    def delete(self, entertainment_id: int) -> None:
        query = text("DELETE FROM travel_db.entertainment WHERE id = :entertainment_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {"entertainment_id": entertainment_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении размещения с ID {entertainment_id}: {e}")
    


