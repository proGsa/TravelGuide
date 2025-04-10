from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.route import Route


Route.model_rebuild()


class IRouteService(ABC):
    @abstractmethod
    async def get_by_id(self, route_id: int) -> Route | None:
        pass
    
    @abstractmethod
    async def get_all_routes(self) -> list[Route]:
        pass

    @abstractmethod
    async def add(self, route: Route) -> Route:
        pass

    @abstractmethod
    async def update(self, updated_route: Route) -> Route:
        pass

    @abstractmethod
    async def delete(self, route_id: int) -> None:
        pass


