from __future__ import annotations

from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


class EntertainmentController:
    def __init__(self, entertainment_service: EntertainmentService) -> None:
        self.entertainment_service = entertainment_service

    async def create_new_entertainment(self, entertainment: Entertainment) -> None:
        try:
            await self.entertainment_service.add(entertainment)
        except Exception as e:
            print(f"Ошибка при создании нового развлечения: {e}s")
    
    async def update_entertainment(self, entertainment: Entertainment) -> None:
        try:
            await self.entertainment_service.update(entertainment)
        except Exception as e:
            print(f"Ошибка при обновлении развлечения: {e}s")
            
    async def get_entertainment_details(self, entertainment_id: int) -> Entertainment | None:
        try:
            return await self.entertainment_service.get_by_id(entertainment_id)
        except Exception as e:
            print(f"Ошибка при получении данных развлечения: {e}s")
        return None

    async def get_all_entertainment(self) -> list[Entertainment]:
        try:
            return await self.entertainment_service.get_list()
        except Exception as e:
            print(f"Ошибка при получении данных развлечения: {e}s")
        return []
    
    async def delete_entertainment(self, entertainment_id: int) -> None:
        try:
            await self.entertainment_service.delete(entertainment_id)
        except Exception as e:
            print(f"Ошибка при обновлении развлечения: {e}s")
    