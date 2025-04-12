from __future__ import annotations

from abstract_service.accommodation_service import IAccommodationService
from models.accommodation import Accommodation
from repository.accommodation_repository import AccommodationRepository


# class AccommodationRepository:
#     def get_by_id(self, accommodation_id: int) -> Accommodation | None:
#         pass

#     def update(self, updated_accommodation: Accommodation) -> None:
#         pass

#     def delete(self, accommodation_id: int) -> None:
#         pass

#     def add(self, accommodation: Accommodation) -> None:
#         pass

#     @staticmethod
#     def get_list() -> list[Accommodation]:


class AccommodationService(IAccommodationService):
    def __init__(self, repository: AccommodationRepository) -> None:
        self.repository = repository

    async def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        return await self.repository.get_by_id(accommodation_id)

    async def get_list(self) -> list[Accommodation]:
        return await self.repository.get_list()

    async def add(self, accommodation: Accommodation) -> Accommodation:
        try:
            await self.repository.add(accommodation)
        except (Exception):
            raise ValueError("Развлечение c таким ID уже существует.")
        return accommodation

    async def update(self, update_accommodation: Accommodation) -> Accommodation:
        try:
            await self.repository.update(update_accommodation)
        except (Exception):
            raise ValueError("Развлечение не найдено.")
        return update_accommodation

    async def delete(self, accommodation_id: int) -> None:
        try:
            await self.repository.delete(accommodation_id)
        except (Exception):
            raise ValueError("Развлечение не найдено.")


