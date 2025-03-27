from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.route import Route


Route.model_rebuild()


class IRouteService(ABC):
    @abstractmethod
    def get_by_id(self, route_id: int) -> Route | None:
        pass
    
    @abstractmethod
    def get_all_routes(self) -> list[Route]:
        pass

    @abstractmethod
    def add(self, route: Route) -> Route:
        pass

    @abstractmethod
    def update(self, updated_route: Route) -> Route:
        pass

    @abstractmethod
    def delete(self, route_id: int) -> None:
        pass


