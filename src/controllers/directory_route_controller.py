from __future__ import annotations

from models.route import Route
from services.city_service import CityService
from services.route_service import RouteService


class RouteController:
    def __init__(self, route_service: RouteService, city_service: CityService) -> None:
        self.route_service = route_service
        self.city_service = city_service

    async def create_new_route(self, route: Route) -> None:
        try:
            await self.route_service.add(route)
        except Exception as e:
            print(f"Ошибка при создании нового маршрута: {e}s")

    async def add_new_city(self, travel_id: int, new_city_id: int, from_city_id: int, to_city_id: int) -> None:
        try:
            await self.route_service.insert_city_between(travel_id, new_city_id, from_city_id, to_city_id)
        except Exception as e:
            print(f"Ошибка при создании нового маршрута: {e}s")

    async def delete_city_from_route(self, city_id: int) -> None:
        try:
            await self.route_service.delete_city_from_route(city_id)
        except Exception as e:
            print(f"Ошибка при удалении города из маршрута: {e}s")
    
    async def update_route(self, route: Route) -> None:
        try:
            await self.route_service.update(route)
        except Exception as e:
            print(f"Ошибка при обновлении маршрута: {e}s")
 
    async def get_route_details(self, route_id: int) -> Route | None:
        try:
            return await self.route_service.get_by_id(route_id)
        except Exception as e:
            print(f"Ошибка при получении данных маршрутов: {e}s")
        return None

    async def change_transport(self, route_id: int, new_transport: str, new_price: int) -> None:
        try:
            await self.route_service.change_transport(route_id, new_transport, new_price)
        except Exception as e:
            print(f"Ошибка при получении данных маршрутов: {e}s")

    async def delete_route(self, route_id: int) -> None:
        try:
            await self.route_service.delete(route_id)
        except Exception as e:
            print(f"Ошибка при удалении маршрута: {e}s")
    