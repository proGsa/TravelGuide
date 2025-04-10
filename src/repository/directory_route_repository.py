from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from models.directory_route import DirectoryRoute
from repository.city_repository import CityRepository


class DirectoryRouteRepository(IDirectoryRouteRepository):
    def __init__(self, session: AsyncSession, city_repo: CityRepository):
        self.session = session
        self.city_repo = city_repo

    async def get_list(self) -> list[DirectoryRoute]:
        query = text("SELECT * FROM directory_route")
        try:
            result = await self.session.execute(query)
            result = result.mappings()
            return [
                DirectoryRoute(
                    d_route_id=row["id"],
                    type_transport=row["type_transport"],
                    cost=row["price"],
                    distance=row["distance"],
                    departure_city=await self.city_repo.get_by_id(row["departure_city"]),
                    destination_city=await self.city_repo.get_by_id(row["arrival_city"])
                )
                for row in result
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка справочника маршрутов: {e}")
            return []

    async def get_by_id(self, directory_route_id: int) -> DirectoryRoute | None:
        query = text("SELECT * FROM directory_route WHERE id = :directory_route_id")
        try:
            result = await self.session.execute(query, {"directory_route_id": directory_route_id})
            result = result.mappings().first()
            if result:
                departure_city = await self.city_repo.get_by_id(result["departure_city"])
                destination_city = await self.city_repo.get_by_id(result["arrival_city"])

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

    async def get_distance(self, from_city_id: int, to_city_id: int) -> int:
        query = text("""
            SELECT * FROM directory_route 
            WHERE departure_city = :from_id AND arrival_city = :to_id
        """)
        try:
            result = await self.session.execute(query, {
                "from_id": from_city_id,
                "to_id": to_city_id
            })
            result = result.mappings().first()
            if result:
                return result["distance"]
            print(f"Маршрут {from_city_id} → {to_city_id} не найден в directory_route")
            return 0
        except SQLAlchemyError:
            print("Ошибка при получении дистанции маршрута")
            return 0

    async def add(self, directory_route: DirectoryRoute) -> None:
        if directory_route.departure_city is None or directory_route.destination_city is None:
            print("Ошибка: Отсутствуют данные о городах")
            return
        query = text("""
            INSERT INTO directory_route (type_transport, price, distance, departure_city, arrival_city)
            VALUES (:type_transport, :price, :distance, :departure_city, :arrival_city)
        """)
        try:
            await self.session.execute(query, {
            "type_transport": directory_route.type_transport,
            "price": directory_route.cost,
            "distance": directory_route.distance,
            "departure_city": directory_route.departure_city.city_id,
            "arrival_city": directory_route.destination_city.city_id
            })
            await self.session.commit()
        except IntegrityError:
            print("Ошибка: такой справочник маршрута уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении справочника маршрутов: {e}")
            await self.session.rollback()

    async def update(self, update_directory_route: DirectoryRoute) -> None:
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
            await self.session.execute(query, {
                "type_transport": update_directory_route.type_transport,
                "price": update_directory_route.cost,
                "distance": update_directory_route.distance,
                "departure_city": update_directory_route.departure_city.city_id,
                "arrival_city": update_directory_route.destination_city.city_id,
                "directory_route_id": update_directory_route.d_route_id
            })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении справочника маршрутов с ID {update_directory_route.d_route_id}: {e}")
            
    async def delete(self, directory_route_id: int) -> None:
        query = text("DELETE FROM directory_route WHERE id = :directory_route_id")
        try:
            await self.session.execute(query, {"directory_route_id": directory_route_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении справочника маршрутов с ID {directory_route_id}: {e}")

    async def get_by_cities(self, from_city_id: int, to_city_id: int) -> DirectoryRoute | None:
        query = text("""
            SELECT * FROM directory_route 
            WHERE departure_city = :from_id AND arrival_city = :to_id
        """)
        try:
            result = await self.session.execute(query, {
                "from_id": from_city_id,
                "to_id": to_city_id
            })
            result = result.mappings().first()
            if result:
                departure_city = await self.city_repo.get_by_id(result["departure_city"])
                destination_city = await self.city_repo.get_by_id(result["arrival_city"])

                return DirectoryRoute(
                    d_route_id=result["id"],
                    type_transport=result["type_transport"],
                    cost=result["price"],
                    distance=result["distance"],
                    departure_city=departure_city,
                    destination_city=destination_city
                )
            return None

        except SQLAlchemyError:
            print("Ошибка при удалении справочника маршрутов по городам")
        return None
    
    async def change_transport(self, d_route_id: int, transport: str, cost: int) -> None:
        query = text("""
            UPDATE directory_route
            SET type_transport = :type_transport,
            price = :price,
            WHERE id = :directory_route_id
        """)
        try:
            await self.session.execute(query, {
                "type_transport": transport,
                "price": cost,
                "directory_route_id": d_route_id
            })
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении справочника маршрутов с ID {d_route_id}: {e}")