from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.city import City


class ICityService(ABC):
    @abstractmethod
    def get_by_id(self, city_id: int) -> City | None:
        pass
    
    @abstractmethod
    def get_all_cities(self) -> list[City]:
        pass
    
    @abstractmethod
    def add(self, city: City) -> City:
        pass
    
    @abstractmethod
    def update(self, updated_city: City) -> City:
        pass
    
    @abstractmethod
    def delete(self, city_id: int) -> None:
        pass
