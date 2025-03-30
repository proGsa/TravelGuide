from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.iroute_repository import IRouteRepository
from models.route import Route
from repository.directory_route_repository import DirectoryRouteRepository
from repository.travel_repository import TravelRepository


class RouteRepository(IRouteRepository):
    def __init__(self, engine: Engine, d_route_repo: DirectoryRouteRepository, travel_repo: TravelRepository):
        self.engine = engine
        self.d_route_repo = d_route_repo
        self.travel_repo = travel_repo

    def get_list(self) -> list[Route]:
        query = text("SELECT * FROM route")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings()
                return [
                    Route(
                        route_id=row["id"],
                        d_route=self.d_route_repo.get_by_id(row["d_route_id"]),
                        travels=self.travel_repo.get_by_id(row["travel_id"]),
                        start_time=row["start_time"],
                        end_time=row["end_time"]
                    )
                    for row in result
                ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка маршрутов: {e}")
            return []

    def get_by_id(self, route_id: int) -> Route | None:
        query = text("SELECT * FROM route WHERE id = :route_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"route_id": route_id}).mappings().first()
                if result:
                    return Route(
                        route_id=result["id"],
                        d_route=self.d_route_repo.get_by_id(result["d_route_id"]),
                        travels=self.travel_repo.get_by_id(result["travel_id"]),
                        start_time=result["start_time"],
                        end_time=result["end_time"]
                    )
                return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении маршрута по ID {route_id}: {e}")
            return None

    def add(self, route: Route) -> None:
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
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                "d_route_id": route.d_route.d_route_id,
                "travel_id": route.travels.travel_id,
                "start_time": route.start_time,
                "end_time": route.end_time
                })

        except IntegrityError:
            print("Ошибка: такой маршрут уже существует.")
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении маршрутов: {e}")

    def update(self, update_route: Route) -> None:
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
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "d_route_id": update_route.d_route.d_route_id,
                    "travel_id": update_route.travels.travel_id,
                    "start_time": update_route.start_time,
                    "end_time": update_route.end_time,
                    "route_id": update_route.route_id 
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении маршрута с ID {update_route.route_id}: {e}")
            
    def delete(self, route_id: int) -> None:
        query = text("DELETE FROM route WHERE id = :route_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {"route_id": route_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении маршрута с ID {route_id}: {e}")

