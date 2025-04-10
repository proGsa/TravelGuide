from __future__ import annotations

from abstract_service.entertainment_service import IEntertainmentService
from models.entertainment import Entertainment
from repository.entertainment_repository import EntertainmentRepository


# class EntertainmentRepository:
#     def get(self, entertainment_id: int) -> Entertainment | None:
#         pass

#     def update(self, updated_entertainment: Entertainment) -> None:
#         pass

#     def delete(self, entertainment_id: int) -> None:
#         pass

#     def add(self, entertainment: Entertainment) -> None:
#         pass
    
#     @staticmethod
#     def get_list() -> list[Entertainment]:


class EntertainmentService(IEntertainmentService):
    def __init__(self, repository: EntertainmentRepository) -> None:
        self.repository = repository

    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        return await self.repository.get_by_id(entertainment_id)

    async def add(self, entertainment: Entertainment) -> Entertainment:
        try:
            await self.repository.add(entertainment)
        except (Exception):
            raise ValueError("Размещение c таким ID уже существует.")
        return entertainment

    async def update(self, update_entertainment: Entertainment) -> Entertainment:
        try:
            await self.repository.update(update_entertainment)
        except (Exception):
            raise ValueError("Размещение не найдено.")
        
        return update_entertainment

    async def delete(self, entertainment_id: int) -> None:
        try:
            await self.repository.delete(entertainment_id)
        except (Exception):
            raise ValueError("Размещение не найдено.")

    async def get_all(self) -> list[Entertainment]:
        return await self.repository.get_list()
