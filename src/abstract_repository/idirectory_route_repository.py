from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.directory_route import DirectoryRoute


class IDirectoryRouteRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[DirectoryRoute]]:
        pass

    @abstractmethod
    def get_by_id(self, directory_route_id: int) -> Coroutine[Any, Any, DirectoryRoute | None]:
        pass

    @abstractmethod
    def add(self, directory_route: DirectoryRoute) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_directory_route: DirectoryRoute) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, directory_route_id: int) -> Coroutine[Any, Any, None]:
        pass
