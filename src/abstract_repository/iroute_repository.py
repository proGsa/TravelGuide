from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.route import Route


class IRouteRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[Route]:
        pass

    @abstractmethod
    async def get_by_id(self, route_id: int) -> Route | None:
        pass

    @abstractmethod
    async def add(self, route: Route) -> None:
        pass

    @abstractmethod
    async def update(self, update_route: Route) -> None:
        pass

    @abstractmethod
    async def delete(self, route_id: int) -> None:
        pass
