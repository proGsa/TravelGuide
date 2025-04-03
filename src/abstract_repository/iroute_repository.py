from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.route import Route


class IRouteRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[Route]]:
        pass

    @abstractmethod
    def get_by_id(self, route_id: int) -> Coroutine[Any, Any, Route | None]:
        pass

    @abstractmethod
    def add(self, route: Route) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_route: Route) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, route_id: int) -> Coroutine[Any, Any, None]:
        pass
