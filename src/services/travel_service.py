from __future__ import annotations

from abstract_service.travel_service import ITravelService
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from repository.travel_repository import TravelRepository


Travel.model_rebuild()


# class TravelRepository:
#     def get(self, travel_id: int) -> Travel | None:
#         pass

#     def update(self, updated_travel: Travel) -> None:
#         pass

#     def delete(self, travel_id: int) -> None:
#         pass

#     def add(self, travel: Travel) -> None:
#         pass

#     @staticmethod
#     def get_list() -> list[Travel]:

#     @staticmethod
#     def search(travel_dict: dict[str, str]) -> list[Travel]:

#     @staticmethod
#     def complete(travel_id: int) -> None:
#         pass
    
#     @staticmethod
#     def check_archive() -> list[Travel]:

class TravelService(ITravelService):
    def __init__(self, repository: TravelRepository) -> None:
        self.repository = repository

    async def get_by_id(self, travel_id: int) -> Travel | None:
        return await self.repository.get_by_id(travel_id)

    async def get_all_travels(self) -> list[Travel]:
        return await self.repository.get_list() 

    async def add(self, travel: Travel) -> Travel:
        try:
            await self.repository.add(travel)
        except (Exception):
            raise ValueError("Путешествие c таким ID уже существует.")
        return travel

    async def update(self, update_travel: Travel) -> Travel:
        try:
            await self.repository.update(update_travel)
        except (Exception):
            raise ValueError("Путешествие не найдено.")
        return update_travel

    async def delete(self, travel_id: int) -> None:
        try:
            await self.repository.delete(travel_id)
        except (Exception):
            raise ValueError("Путешествие не найдено.")

    async def search(self, travel_dict: dict[str, str]) -> list[Travel]:
        try:
            return await self.repository.search(travel_dict)
        except (Exception):
            raise ValueError("Путешествие по переданным параметрам не найдено.")
    
    async def complete(self, travel_id: int) -> None:
        try:
            await self.repository.complete(travel_id)
        except (Exception):
            raise ValueError("Ошибка при завершении путешествия")

    async def check_archive(self) -> list[Travel]:
        try:
            return await self.repository.check_archive()
        except (Exception):
            raise ValueError("Ошибка при получении завершенных путешествий")

    async def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        try:
            return await self.repository.get_entertainments_by_travel(travel_id)
        except (Exception):
            raise ValueError("Ошибка при получении завершенных путешествий")

    async def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        try:
            return await self.repository.get_accommodations_by_travel(travel_id)
        except (Exception):
            raise ValueError("Ошибка при получении завершенных путешествий")
