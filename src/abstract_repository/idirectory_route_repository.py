from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.directory_route import DirectoryRoute


class IDirectoryRouteRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[DirectoryRoute]:
        pass

    @abstractmethod
    async def get_by_id(self, directory_route_id: int) -> DirectoryRoute | None:
        pass

    @abstractmethod
    async def add(self, directory_route: DirectoryRoute) -> None:
        pass

    @abstractmethod
    async def update(self, update_directory_route: DirectoryRoute) -> None:
        pass

    @abstractmethod
    async def delete(self, directory_route_id: int) -> None:
        pass
