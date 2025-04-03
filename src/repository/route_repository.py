from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.iroute_repository import IRouteRepository
from models.route import Route
from repository.directory_route_repository import DirectoryRouteRepository
from repository.travel_repository import TravelRepository


class RouteRepository(IRouteRepository):
    def __init__(self, session: AsyncSession, d_route_repo: DirectoryRouteRepository, travel_repo: TravelRepository):
        self.session = session
        self.d_route_repo = d_route_repo
        self.travel_repo = travel_repo

    async def get_list(self) -> list[Route]:
        query = text("SELECT * FROM route")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                Route(
                    route_id=row["id"],
                    d_route=await self.d_route_repo.get_by_id(row["d_route_id"]),
                    travels=await self.travel_repo.get_by_id(row["travel_id"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"]
                )
                for row in result
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка маршрутов: {e}")
            return []

    async def get_by_id(self, route_id: int) -> Route | None:
        query = text("SELECT * FROM route WHERE id = :route_id")
        try:
            result = await self.session.execute(query, {"route_id": route_id})
            result = result.mappings().first()
            if result:
                return Route(
                    route_id=result["id"],
                    d_route=await self.d_route_repo.get_by_id(result["d_route_id"]),
                    travels=await self.travel_repo.get_by_id(result["travel_id"]),
                    start_time=result["start_time"],
                    end_time=result["end_time"]
                )
            return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении маршрута по ID {route_id}: {e}")
            return None

    async def add(self, route: Route) -> None:
        if route.travels is None:
            print("Ошибка: Отсутствуют данные о путешествии")
            return
        if route.d_route is None:
            print("Ошибка: Отсутствуют данные о справочнике путешествий")
            return
        query = text("""
            INSERT INTO route (d_route_id, travel_id, start_time, end_time)
            VALUES (:d_route_id, :travel_id, :start_time, :end_time)
        """)
        try:
            await self.session.execute(query, {
            "d_route_id": route.d_route.d_route_id,
            "travel_id": route.travels.travel_id,
            "start_time": route.start_time,
            "end_time": route.end_time
            })
            await self.session.commit()
        except IntegrityError:
            print("Ошибка: такой маршрут уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении маршрутов: {e}")
            await self.session.rollback()

    async def update(self, update_route: Route) -> None:
        if update_route.travels is None:
            print("Ошибка: Отсутствуют данные о путешествии")
            return
        if update_route.d_route is None:
            print("Ошибка: Отсутствуют данные о справочнике путешествий")
            return
        query = text("""
            UPDATE route
            SET d_route_id = :d_route_id,
            travel_id = :travel_id,
            start_time = :start_time,
            end_time = :end_time
        WHERE id = :route_id
        """)
        try:
            await self.session.execute(query, {
                "d_route_id": update_route.d_route.d_route_id,
                "travel_id": update_route.travels.travel_id,
                "start_time": update_route.start_time,
                "end_time": update_route.end_time,
                "route_id": update_route.route_id 
            })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении маршрута с ID {update_route.route_id}: {e}")
            
    async def delete(self, route_id: int) -> None:
        query = text("DELETE FROM route WHERE id = :route_id")
        try:
            await self.session.execute(query, {"route_id": route_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении маршрута с ID {route_id}: {e}")

