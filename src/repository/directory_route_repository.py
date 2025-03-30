from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from models.directory_route import DirectoryRoute
from repository.city_repository import CityRepository


class DirectoryRouteRepository(IDirectoryRouteRepository):
    def __init__(self, engine: Engine, city_repo: CityRepository):
        self.engine = engine
        self.city_repo = city_repo

    def get_list(self) -> list[DirectoryRoute]:
        query = text("SELECT * FROM directory_route")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings()
                return [
                    DirectoryRoute(
                        d_route_id=row["id"],
                        type_transport=row["type_transport"],
                        cost=row["price"],
                        distance=row["distance"],
                        departure_city=self.city_repo.get_by_id(row["departure_city"]),
                        destination_city=self.city_repo.get_by_id(row["arrival_city"])
                    )
                    for row in result
                ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка справочника маршрутов: {e}")
            return []

    def get_by_id(self, directory_route_id: int) -> DirectoryRoute | None:
        query = text("SELECT * FROM directory_route WHERE id = :directory_route_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"directory_route_id": directory_route_id}).mappings().first()
                if result:
                    departure_city = self.city_repo.get_by_id(result["departure_city"])
                    destination_city = self.city_repo.get_by_id(result["arrival_city"])

                    return DirectoryRoute(
                        d_route_id=result["id"],
                        type_transport=result["type_transport"],
                        cost=result["price"],
                        distance=result["distance"],
                        departure_city=departure_city,
                        destination_city=destination_city
                    )
                return None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении справочника маршрутов по ID {directory_route_id}: {e}")
            return None

    def add(self, directory_route: DirectoryRoute) -> None:
        if directory_route.departure_city is None or directory_route.destination_city is None:
            print("Ошибка: Отсутствуют данные о городах")
            return
        query = text("""
            INSERT INTO directory_route (type_transport, price, distance, departure_city, arrival_city)
            VALUES (:type_transport, :price, :distance, :departure_city, :arrival_city)
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                "type_transport": directory_route.type_transport,
                "price": directory_route.cost,
                "distance": directory_route.distance,
                "departure_city": directory_route.departure_city.city_id,
                "arrival_city": directory_route.destination_city.city_id
                })
        except IntegrityError:
            print("Ошибка: такой справочник маршрута уже существует.")
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении справочника маршрутов: {e}")

    def update(self, update_directory_route: DirectoryRoute) -> None:
        if update_directory_route.departure_city is None or update_directory_route.destination_city is None:
            print("Ошибка: Отсутствуют данные о городах")
            return
        query = text("""
            UPDATE directory_route
            SET type_transport = :type_transport,
                price = :price,
                distance = :distance,
                departure_city = :departure_city,
                arrival_city = :arrival_city
            WHERE id = :directory_route_id
        """)
        try:
            with self.engine.connect() as conn, conn.begin():
                conn.execute(query, {
                    "type_transport": update_directory_route.type_transport,
                    "price": update_directory_route.cost,
                    "distance": update_directory_route.distance,
                    "departure_city": update_directory_route.departure_city.city_id,
                    "arrival_city": update_directory_route.destination_city.city_id,
                    "directory_route_id": update_directory_route.d_route_id
                })
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении справочника маршрутов с ID {update_directory_route.d_route_id}: {e}")
            
    def delete(self, directory_route_id: int) -> None:
        query = text("DELETE FROM directory_route WHERE id = :directory_route_id")
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {"directory_route_id": directory_route_id})
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении справочника маршрутов с ID {directory_route_id}: {e}")


