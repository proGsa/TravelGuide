from __future__ import annotations

from abstract_service.route_service import IRouteService
from models.route import Route
from repository.route_repository import RouteRepository


Route.model_rebuild()


# class RouteRepository:
#     def get(self, route_id: int) -> Route | None:
#         pass

#     def update(self, updated_route: Route) -> None:
#         pass

#     def delete(self, route_id: int) -> None:
#         pass

#     def add(self, route: Route) -> None:
#         pass
    
#     @staticmethod
#     def values() -> list[Route]:


class RouteService(IRouteService):
    def __init__(self, repository: RouteRepository) -> None:
        self.repository = repository

    async def get_by_id(self, route_id: int) -> Route | None:
        return await self.repository.get_by_id(route_id)

    async def get_all_routes(self) -> list[Route]:
        return await self.repository.get_list()

    async def add(self, route: Route) -> Route:
        try:
            await self.repository.add(route)
        except (Exception):
            raise ValueError("Маршрут c таким ID уже существует.")
        
        return route

    async def update(self, updated_route: Route) -> Route:
        try:
            await self.repository.update(updated_route)
        except (Exception):
            raise ValueError("Маршрут не найден.")

        return updated_route

    async def delete(self, route_id: int) -> None:
        try:
            await self.repository.delete(route_id)
        except (Exception):
            raise ValueError("Маршрут не найден.")

    async def insert_city_between(self, travel_id: int, new_city_id: int, from_city_id: int, to_city_id: int) -> None:
        try:
            await self.repository.insert_city_between(travel_id, new_city_id, from_city_id, to_city_id)
        except (Exception):
            raise ValueError("Город не получилось добавить.")

    async def delete_city_from_route(self, city_id: int) -> None:
        try:
            await self.repository.delete_city_from_route(city_id)
        except (Exception):
            raise ValueError("Город не получилось удалить из маршрута.")

    async def change_transport(self, route_id: int, new_transport: str, new_price: int) -> None:
        try:
            await self.repository.change_transport(route_id, new_transport, new_price)
        except (Exception):
            raise ValueError("Город не получилось удалить из маршрута.")