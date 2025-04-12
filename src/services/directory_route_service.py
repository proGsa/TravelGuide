from __future__ import annotations

from abstract_service.directory_route_service import IDirectoryRouteService
from models.directory_route import DirectoryRoute
from repository.directory_route_repository import DirectoryRouteRepository


# class DirectoryRouteRepository:
#     def get(self, directory_route_id: int) -> DirectoryRoute | None:
#         pass

#     def update(self, updated_directory_route: DirectoryRoute) -> None:
#         pass

#     def delete(self, directory_route_id: int) -> None:
#         pass

#     def add(self, directory_route: DirectoryRoute) -> None:
#         pass


class DirectoryRouteService(IDirectoryRouteService):
    def __init__(self, repository: DirectoryRouteRepository) -> None:
        self.repository = repository

    async def get_by_id(self, d_route_id: int) -> DirectoryRoute | None:
        return await self.repository.get_by_id(d_route_id)

    async def add(self, d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            await self.repository.add(d_route)
        except (Exception):
            raise ValueError("Cпpaвoчник маршрутов c таким ID уже существует.")

        return d_route

    async def update(self, updated_d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            await self.repository.update(updated_d_route)
        except (Exception):
            raise ValueError("Cпpaвoчник маршрутов не найден.")
        
        return updated_d_route

    async def delete(self, d_route_id: int) -> None:
        try:
            await self.repository.delete(d_route_id)
        except (Exception):
            raise ValueError("Cпpaвoчник маршрутов не получилось удалить.")

    async def change_transport(self, d_route_id: int, transport: str, cost: int) -> None:
        try:
            await self.repository.change_transport(d_route_id, transport, cost)
        except (Exception):
            raise ValueError("Не получилось изменить транспорт.")