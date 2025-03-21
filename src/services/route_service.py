from __future__ import annotations

from models.route import Route


Route.model_rebuild()


class RouteRepository:
    def get(self, route_id: int) -> Route | None:
        pass

    def update(self, updated_route: Route) -> None:
        pass

    def delete(self, route_id: int) -> None:
        pass

    def add(self, route: Route) -> None:
        pass
    
    @staticmethod
    def values() -> list[Route]:
        return []


class RouteService:
    def __init__(self, repository: RouteRepository) -> None:
        self.repository = repository

    def get_by_id(self, route_id: int) -> Route | None:
        return self.repository.get(route_id)

    def get_all_routes(self) -> list[Route]:
        return list(self.repository.values()) 

    def add(self, route: Route) -> Route:
        try:
            self.repository.add(route)
        except (Exception):
            raise ValueError("Маршрут c таким ID уже существует.")
        
        return route

    def update(self, updated_route: Route) -> Route:
        try:
            self.repository.update(updated_route)
        except (Exception):
            raise ValueError("Маршрут не найден.")

        return updated_route

    def delete(self, route_id: int) -> None:
        try:
            self.repository.delete(route_id)
        except (Exception):
            raise ValueError("Маршрут не найден.")


