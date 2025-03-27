from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.directory_route import DirectoryRoute


class IDirectoryRouteService(ABC):
    @abstractmethod
    def get_by_id(self, d_route_id: int) -> DirectoryRoute | None:
        pass

    @abstractmethod
    def add(self, d_route: DirectoryRoute) -> DirectoryRoute:
        pass

    @abstractmethod
    def update(self, updated_d_route: DirectoryRoute) -> DirectoryRoute:
        pass

    @abstractmethod
    def delete(self, d_route_id: int) -> None:
        pass

