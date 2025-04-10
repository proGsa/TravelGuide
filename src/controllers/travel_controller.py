from __future__ import annotations

from typing import Any

from models.travel import Travel
from services.travel_service import TravelService


class TravelController:
    def __init__(self, travel_service: TravelService) -> None:
        self.travel_service = travel_service

    async def create_new_travel(self, travel: Travel) -> None:
        try:
            await self.travel_service.add(travel)
        except Exception as e:
            print(f"Ошибка при создании нового путешествия: {e}s")

    async def get_travel_details(self, travel_id: int) -> Travel | None:
        try:
            return await self.travel_service.get_by_id(travel_id)
        except Exception as e:
            print(f"Ошибка при получении данных путешествия: {e}")
        return None

    async def complete_travel(self, travel_id: int) -> None:
        try:
            return await self.travel_service.complete(travel_id)
        except Exception as e:
            print(f"Ошибка при завершении путешествия: {e}")
        return None

    async def check_archive_travels(self) -> list[Travel]:
        try:
            return await self.travel_service.check_archive()
        except Exception as e:
            print(f"Ошибка при завершении путешествия: {e}")
        return []

    async def update_travel(self, travel: Travel) -> None:
        try:
            await self.travel_service.update(travel)
        except Exception as e:
            print(f"Ошибка при обновлении путешествия: {e}")

    async def search_travel(self, travel_dict: dict[str, Any]) -> list[Travel]: 
        try:
            return await self.travel_service.search(travel_dict)
        except Exception as e:
            print(f"Ошибка при поиске путешествия: {e}")
        return []