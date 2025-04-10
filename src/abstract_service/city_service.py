from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.city import City


class ICityService(ABC):
    @abstractmethod
    async def get_by_id(self, city_id: int) -> City | None:
        pass
    
    @abstractmethod
    async def get_all_cities(self) -> list[City]:
        pass
    
    @abstractmethod
    async def add(self, city: City) -> City:
        pass
    
    @abstractmethod
    async def update(self, updated_city: City) -> City:
        pass
    
    @abstractmethod
    async def delete(self, city_id: int) -> None:
        pass
