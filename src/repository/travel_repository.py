from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.itravel_repository import ITravelRepository
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from repository.accommodation_repository import AccommodationRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.user_repository import UserRepository


class TravelRepository(ITravelRepository):
    def __init__(self, session: AsyncSession, user_repo: UserRepository, e_repo: EntertainmentRepository, 
                                                                a_repo: AccommodationRepository):
        self.session = session
        self.user_repo = user_repo
        self.entertainment_repo = e_repo
        self.accommodation_repo = a_repo

    async def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        query = text("SELECT accommodation_id FROM travel_accommodations WHERE travel_id = :travel_id")
        try:
            result = await self.session.execute(query, {"travel_id": travel_id})
            result = result.fetchall()

            end_list = []
            for row in result:
                acc = await self.accommodation_repo.get_by_id(row[0])
                if acc is not None:
                    end_list.append(acc)
            return end_list
        except SQLAlchemyError as e:
            print(f"Ошибка при получении размещения для путешествия {travel_id}: {e}")
            return []
    
    async def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        query = text("SELECT entertainment_id FROM travel_entertainment WHERE travel_id = :travel_id")
        try:
            result = await self.session.execute(query, {"travel_id": travel_id})
            result = result.fetchall()

            ent_list = []
            for row in result:
                ent = await self.entertainment_repo.get_by_id(row[0])
                if ent is not None:
                    ent_list.append(ent)

            return ent_list
        except SQLAlchemyError as e:
            print(f"Ошибка при получении развлечений в путешествие {travel_id}: {e}")
            return []

    async def get_list(self) -> list[Travel]:
        query = text("SELECT * FROM travel")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                Travel(
                    travel_id=row["id"],
                    status=row["status"],
                    users=await self.user_repo.get_by_id(row["user_id"]),
                    entertainments=await self.get_entertainments_by_travel(row["id"]),
                    accommodations=await self.get_accommodations_by_travel(row["id"])
                )
                for row in result
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка путешествий: {e}")
            return []

    async def get_by_id(self, travel_id: int) -> Travel | None:
        query = text("SELECT * FROM travel WHERE id = :travel_id")
        try:
            result = await self.session.execute(query, {"travel_id": travel_id})
            result = result.mappings().first()
            if result:
                return Travel(
                    travel_id=result["id"],
                    status=result["status"],
                    users=await self.user_repo.get_by_id(result["user_id"]),
                    entertainments=await self.get_entertainments_by_travel(result["id"]),
                    accommodations=await self.get_accommodations_by_travel(result["id"])
                )
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении путешествия по ID {travel_id}: {e}")
            return None

    async def add(self, travel: Travel) -> None:
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
            result = await self.session.execute(query, {
                "status": travel.status,
                "user_id": travel.users.user_id
            })
            travel_id = result.scalar_one()

            if travel.entertainments:
                for ent in travel.entertainments:
                    try:
                        await self.session.execute(entertainment_query, {
                            "travel_id": travel_id,
                            "entertainment_id": ent.entertainment_id
                        })
                    except SQLAlchemyError as e:
                        print(f"Ошибка при добавлении развлечения с ID {ent.entertainment_id}: {e}")

            if travel.accommodations:
                for acc in travel.accommodations:
                    try:
                        await self.session.execute(accommodation_query, {
                            "travel_id": travel_id,
                            "accommodation_id": acc.accommodation_id
                        })
                    except SQLAlchemyError as e:
                        print(f"Ошибка при добавлении размещения с ID {acc.accommodation_id}: {e}")
            await self.session.commit()               
        except IntegrityError:
            print("Ошибка: такое путешествие уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении путешествия: {e}")
            await self.session.rollback()

    async def update(self, update_travel: Travel) -> None:
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
            result = await self.session.execute(check_query, {"travel_id": update_travel.travel_id})
            if result.fetchone() is None:
                print(f"Путешествие с ID {update_travel.travel_id} не существует.")
                return
            await self.session.execute(update_travel_query, {
                "status": update_travel.status,
                "user_id": update_travel.users.user_id,
                "travel_id": update_travel.travel_id
            })

            await self.session.execute(delete_entertainments_query, {"travel_id": update_travel.travel_id})
            await self.session.execute(delete_accommodations_query, {"travel_id": update_travel.travel_id})

            if update_travel.entertainments:
                for ent in update_travel.entertainments:
                    try:
                        await self.session.execute(entertainment_query, {
                            "travel_id": update_travel.travel_id,
                            "entertainment_id": ent.entertainment_id
                        })
                    except SQLAlchemyError as e:
                        print(f"Ошибка при добавлении развлечения с ID {ent.entertainment_id}: {e}")

            if update_travel.accommodations:
                for acc in update_travel.accommodations:
                    try:
                        await self.session.execute(accommodation_query, {
                            "travel_id": update_travel.travel_id,
                            "accommodation_id": acc.accommodation_id
                        })
                    except SQLAlchemyError as e:
                        print(f"Ошибка при добавлении размещения с ID {acc.accommodation_id}: {e}")
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении путешествия с ID {update_travel.travel_id}: {e}")
            
    async def delete(self, travel_id: int) -> None:
        delete_entertainments_query = text("""
            DELETE FROM travel_entertainment WHERE travel_id = :travel_id
        """)

        delete_accommodations_query = text("""
            DELETE FROM travel_accommodations WHERE travel_id = :travel_id
        """)

        query = text("DELETE FROM travel WHERE id = :travel_id")
        try:
            await self.session.execute(delete_entertainments_query, {"travel_id": travel_id})
            await self.session.execute(delete_accommodations_query, {"travel_id": travel_id})
            await self.session.execute(query, {"travel_id": travel_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении путешествия с ID {travel_id}: {e}")
    
