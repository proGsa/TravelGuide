from __future__ import annotations

from models.accommodation import Accommodation
from services.accommodation_service import AccommodationService


class AccommodationController:
    def __init__(self, accommodation_service: AccommodationService) -> None:
        self.accommodation_service = accommodation_service

    async def create_new_accommodation(self, accommodation: Accommodation) -> None:
        try:
            await self.accommodation_service.add(accommodation)
        except Exception as e:
            print(f"Ошибка при создании нового размещения: {e}s")
    
    async def update_accommodation(self, accommodation: Accommodation) -> None:
        try:
            await self.accommodation_service.update(accommodation)
        except Exception as e:
            print(f"Ошибка при обновлении размещения: {e}s")
    
    async def get_accommodation_details(self, accommodation_id: int) -> Accommodation | None:
        try:
            return await self.accommodation_service.get_by_id(accommodation_id)
        except Exception as e:
            print(f"Ошибка при получении данных размещения: {e}s")
        return None

    async def get_all_accommodation(self) -> list[Accommodation]:
        try:
            return await self.accommodation_service.get_list()
        except Exception as e:
            print(f"Ошибка при получении данных размещения: {e}s")
        return []
    
    async def delete_accommodation(self, accommodation_id: int) -> None:
        try:
            await self.accommodation_service.delete(accommodation_id)
        except Exception as e:
            print(f"Ошибка при обновлении размещения: {e}s")
    