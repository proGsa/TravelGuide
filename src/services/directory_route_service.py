from __future__ import annotations

from abstract_service.directory_route_service import IDirectoryRouteService
from models.directory_route import DirectoryRoute


class DirectoryRouteRepository:
    def get(self, directory_route_id: int) -> DirectoryRoute | None:
        pass

    def update(self, updated_directory_route: DirectoryRoute) -> None:
        pass

    def delete(self, directory_route_id: int) -> None:
        pass

    def add(self, directory_route: DirectoryRoute) -> None:
        pass


class DirectoryRouteService(IDirectoryRouteService):
    def __init__(self, repository: DirectoryRouteRepository) -> None:
        self.repository = repository

    def get_by_id(self, d_route_id: int) -> DirectoryRoute | None:
        return self.repository.get(d_route_id)

    def add(self, d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            self.repository.add(d_route)
        except (Exception):
            raise ValueError("Cпpaвoчник маршрутов c таким ID уже существует.")

        return d_route

    def update(self, updated_d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            self.repository.update(updated_d_route)
        except (Exception):
            raise ValueError("Cпpaвoчник маршрутов не найден.")
        
        return updated_d_route

    def delete(self, d_route_id: int) -> None:
        try:
            self.repository.delete(d_route_id)
        except (Exception):
            raise ValueError("Пользователь не найден.")

