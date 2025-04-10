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

    async def get_routes_by_travel_id_ordered(self, travel_id: int) -> list[Route]:
        query = text("""
            SELECT * FROM route 
            WHERE travel_id = :travel_id
            ORDER BY start_time
        """)
        try:
            result = await self.session.execute(query, {"travel_id": travel_id})
            rows = result.mappings().all()
            return [
                Route(
                    route_id=row["id"],
                    d_route=await self.d_route_repo.get_by_id(row["d_route_id"]),
                    travels=await self.travel_repo.get_by_id(row["travel_id"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"]
                )
                for row in rows
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении маршрута с travel ID {travel_id}: {e}")
        return []
    
    async def insert_city_between(self, travel_id: int, new_city_id: int, from_city_id: int, to_city_id: int) -> None:
        routes = await self.get_routes_by_travel_id_ordered(travel_id)
        if not routes:
            print("Невозможно вставить город в пустой маршрут.")
            return

        target_route = None
        
        for route in routes:
            if (route.d_route is not None and 
                (route.d_route.departure_city is not None and 
                    route.d_route.destination_city is not None) and 
                (route.d_route.departure_city.city_id == from_city_id and
                    route.d_route.destination_city.city_id == to_city_id)):
                target_route = route
                break

        if not target_route:
            print(f"Маршрут между городами {from_city_id} и {to_city_id} не найден.")
            return

        d1 = await self.d_route_repo.get_by_cities(from_city_id, new_city_id)
        d2 = await self.d_route_repo.get_by_cities(new_city_id, to_city_id)

        if not d1 or not d2:
            print("Ошибка: нет маршрута между выбранными городами.")
            return

        await self.delete(target_route.route_id)

        route1 = Route(
            route_id=1,
            d_route=d1,
            travels=target_route.travels,
            start_time=target_route.start_time,
            end_time=target_route.end_time 
        )
        route2 = Route(
            route_id=2,
            d_route=d2,
            travels=target_route.travels,
            start_time=target_route.start_time,
            end_time=target_route.end_time
        )

        await self.add(route1)
        await self.add(route2)
        await self.session.commit()

    async def get_routes_by_city(self, city_id: int) -> list[Route]:
        query = text("""
            SELECT * 
            FROM route r
            JOIN directory_route dr ON r.d_route_id = dr.id
            WHERE departure_city = :city_id OR arrival_city = :city_id
        """)
        try:
            result = await self.session.execute(query, {"city_id": city_id})
            rows = result.mappings().all()
            
            return [
                Route(
                    route_id=row["id"],
                    d_route=await self.d_route_repo.get_by_id(row["d_route_id"]),
                    travels=await self.travel_repo.get_by_id(row["travel_id"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"]
                )
                for row in rows
            ]
        
        except SQLAlchemyError as e:
            print(f"Ошибка при получении маршрутов для города с ID {city_id}: {e}")
            return []

    async def delete_city_from_route(self, city_id: int) -> None:
        routes = await self.get_routes_by_city(city_id)
        for route in routes:
            await self.delete(route.route_id)
        query = text("""
            DELETE FROM directory_route
            WHERE departure_city = :city_id OR arrival_city = :city_id
        """)
        try:
            await self.session.execute(query, {"city_id": city_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении записей из directory_route для города с ID {city_id}: {e}")

    async def change_transport(self, route_id: int, new_transport: str, new_price: int) -> None:
        try:
            route_query = text("""
                SELECT * 
                FROM travel_db.route 
                WHERE id = :route_id
            """)
            result = await self.session.execute(route_query, {"route_id": route_id})
            route = result.mappings().first()

            if not route:
                print(f"Ошибка: Маршрут с ID {route_id} не найден.")
                return

            d_route_id = route["d_route_id"]

            await self.d_route_repo.change_transport(d_route_id, new_transport, new_price)
            await self.session.commit()
            
        except SQLAlchemyError as e:
            print(f"Ошибка при изменении транспорта: {e}")
            await self.session.rollback()