from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.itravel_repository import ITravelRepository
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from repository.accommodation_repository import AccommodationRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.user_repository import UserRepository


class TravelRepository(ITravelRepository):
    def __init__(self, engine: Engine, user_repo: UserRepository, e_repo: EntertainmentRepository, 
                                                                a_repo: AccommodationRepository):
        self.engine = engine
        self.user_repo = user_repo
        self.entertainment_repo = e_repo
        self.accommodation_repo = a_repo

    def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        query = text("SELECT accommodation_id FROM travel_accommodations WHERE travel_id = :travel_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"travel_id": travel_id}).mappings()
                return [
                    acc for acc in (self.accommodation_repo.get_by_id(row["accommodation_id"]) for row in result)
                    if acc is not None
                ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении размещения для путешествия {travel_id}: {e}")
            return []
    
    def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        query = text("SELECT entertainment_id FROM travel_entertainment WHERE travel_id = :travel_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"travel_id": travel_id}).mappings()
                return [
                    ent for ent in (self.entertainment_repo.get_by_id(row["entertainment_id"]) for row in result)
                    if ent is not None
                ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении развлечений для путешествия {travel_id}: {e}")
            return []

    def get_list(self) -> list[Travel]:
        query = text("SELECT * FROM travel")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings()
                return [
                    Travel(
                        travel_id=row["id"],
                        status=row["status"],
                        users=self.user_repo.get_by_id(row["user_id"]),
                        entertainments=self.get_entertainments_by_travel(row["id"]),
                        accommodations=self.get_accommodations_by_travel(row["id"])
                    )
                    for row in result
                ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка путешествий: {e}")
            return []

    def get_by_id(self, travel_id: int) -> Travel | None:
        query = text("SELECT * FROM travel WHERE id = :travel_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"travel_id": travel_id}).mappings().first()
                if result:
                    return Travel(
                        travel_id=result["id"],
                        status=result["status"],
                        users=self.user_repo.get_by_id(result["user_id"]),
                        entertainments=self.get_entertainments_by_travel(result["id"]),
                        accommodations=self.get_accommodations_by_travel(result["id"])
                    )
                return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении путешествия по ID {travel_id}: {e}")
            return None

    def add(self, travel: Travel) -> None:
        if travel.users is None:
            print("Ошибка: Отсутствуют данные о пользователях")
            return
        query = text("""
            INSERT INTO travel (status, user_id)
            VALUES (:status, :user_id)
            RETURNING id
        """)
        entertainment_query = text("""
            INSERT INTO travel_entertainment (travel_id, entertainment_id)
            VALUES (:travel_id, :entertainment_id)
        """)

        accommodation_query = text("""
            INSERT INTO travel_accommodations (travel_id, accommodation_id)
            VALUES (:travel_id, :accommodation_id)
        """)

        try:
            with self.engine.connect() as conn, conn.begin():
                result = conn.execute(query, {
                    "status": travel.status,
                    "user_id": travel.users.user_id
                })
                travel_id = result.scalar_one()

                if travel.entertainments:
                    for ent in travel.entertainments:
                        try:
                            conn.execute(entertainment_query, {
                                "travel_id": travel_id,
                                "entertainment_id": ent.entertainment_id
                            })
                        except SQLAlchemyError as e:
                            print(f"Ошибка при добавлении развлечения с ID {ent.entertainment_id}: {e}")

                if travel.accommodations:
                    for acc in travel.accommodations:
                        try:
                            conn.execute(accommodation_query, {
                                "travel_id": travel_id,
                                "accommodation_id": acc.accommodation_id
                            })
                        except SQLAlchemyError as e:
                            print(f"Ошибка при добавлении размещения с ID {acc.accommodation_id}: {e}")
                                
        except IntegrityError:
            print("Ошибка: такое путешествие уже существует.")
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении путешествия: {e}")

    def update(self, update_travel: Travel) -> None:
        if update_travel.users is None:
            print("Ошибка: Отсутствуют данные о пользователях")
            return
        check_query = text("""
            SELECT 1 FROM travel WHERE id = :travel_id
        """)
        update_travel_query = text("""
            UPDATE travel
            SET status = :status,
                user_id = :user_id
            WHERE id = :travel_id
        """)

        delete_entertainments_query = text("""
            DELETE FROM travel_entertainment WHERE travel_id = :travel_id
        """)
        
        delete_accommodations_query = text("""
            DELETE FROM travel_accommodations WHERE travel_id = :travel_id
        """)

        entertainment_query = text("""
            INSERT INTO travel_entertainment (travel_id, entertainment_id)
            VALUES (:travel_id, :entertainment_id)
        """)

        accommodation_query = text("""
            INSERT INTO travel_accommodations (travel_id, accommodation_id)
            VALUES (:travel_id, :accommodation_id)
        """)

        try:
            with self.engine.connect() as conn, conn.begin():
                result = conn.execute(check_query, {"travel_id": update_travel.travel_id})
                if result.fetchone() is None:
                    print(f"Путешествие с ID {update_travel.travel_id} не существует.")
                    return
                conn.execute(update_travel_query, {
                    "status": update_travel.status,
                    "user_id": update_travel.users.user_id,
                    "travel_id": update_travel.travel_id
                })

                conn.execute(delete_entertainments_query, {"travel_id": update_travel.travel_id})
                conn.execute(delete_accommodations_query, {"travel_id": update_travel.travel_id})

                if update_travel.entertainments:
                    for ent in update_travel.entertainments:
                        try:
                            conn.execute(entertainment_query, {
                                "travel_id": update_travel.travel_id,
                                "entertainment_id": ent.entertainment_id
                            })
                        except SQLAlchemyError as e:
                            print(f"Ошибка при добавлении развлечения с ID {ent.entertainment_id}: {e}")

                if update_travel.accommodations:
                    for acc in update_travel.accommodations:
                        try:
                            conn.execute(accommodation_query, {
                                "travel_id": update_travel.travel_id,
                                "accommodation_id": acc.accommodation_id
                            })
                        except SQLAlchemyError as e:
                            print(f"Ошибка при добавлении размещения с ID {acc.accommodation_id}: {e}")

        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении путешествия с ID {update_travel.travel_id}: {e}")
            
    def delete(self, travel_id: int) -> None:
        delete_entertainments_query = text("""
            DELETE FROM travel_entertainment WHERE travel_id = :travel_id
        """)

        delete_accommodations_query = text("""
            DELETE FROM travel_accommodations WHERE travel_id = :travel_id
        """)

        query = text("DELETE FROM travel WHERE id = :travel_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(delete_entertainments_query, {"travel_id": travel_id})
                conn.execute(delete_accommodations_query, {"travel_id": travel_id})
                conn.execute(query, {"travel_id": travel_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении путешествия с ID {travel_id}: {e}")
    
