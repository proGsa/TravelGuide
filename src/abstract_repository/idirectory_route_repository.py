from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.directory_route import DirectoryRoute


class IDirectoryRouteRepository(ABC):
    @abstractmethod
    def get_list(self) -> list[DirectoryRoute]:
        pass

    @abstractmethod
    def get_by_id(self, directory_route_id: int) -> DirectoryRoute | None:
        pass

    @abstractmethod
    def add(self, directory_route: DirectoryRoute) -> None:
        pass

    @abstractmethod
    def update(self, update_directory_route: DirectoryRoute) -> None:
        pass

    @abstractmethod
    def delete(self, directory_route_id: int) -> None:
        pass
