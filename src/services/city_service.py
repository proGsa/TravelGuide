from __future__ import annotations

from abstract_service.city_service import ICityService
from models.city import City
from repository.city_repository import CityRepository


# class CityRepository:
#     def get(self, city_id: int) -> City | None:
#         pass

#     def update(self, updated_city: City) -> None:
#         pass

#     def delete(self, city_id: int) -> None:
#         pass

#     def add(self, city: City) -> None:
#         pass
    
#     @staticmethod
#     def values() -> list[City]:


class CityService(ICityService):
    def __init__(self, repository: CityRepository) -> None:
        self.repository = repository

    async def get_by_id(self, city_id: int) -> City | None:
        return await self.repository.get_by_id(city_id)

    async def get_all_cities(self) -> list[City]:
        return await self.repository.get_list() 

    async def add(self, city: City) -> City:
        try:
            await self.repository.add(city)
        except (Exception):
            raise ValueError("Город c таким ID уже существует.")
        return city

    async def update(self, updated_city: City) -> City:
        try:
            await self.repository.update(updated_city)
        except (Exception):
            raise ValueError("Город не найден.")
        
        return updated_city

    async def delete(self, city_id: int) -> None:
        try:
            await self.repository.delete(city_id)
        except (Exception):
            raise ValueError("Город не найден.")
