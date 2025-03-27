from __future__ import annotations

from abstract_service.city_service import ICityService
from models.city import City


class CityRepository:
    def get(self, city_id: int) -> City | None:
        pass

    def update(self, updated_city: City) -> None:
        pass

    def delete(self, city_id: int) -> None:
        pass

    def add(self, city: City) -> None:
        pass
    
    @staticmethod
    def values() -> list[City]:
        return []


class CityService(ICityService):
    def __init__(self, repository: CityRepository) -> None:
        self.repository = repository

    def get_by_id(self, city_id: int) -> City | None:
        return self.repository.get(city_id)

    def get_all_cities(self) -> list[City]:
        return list(self.repository.values()) 

    def add(self, city: City) -> City:
        try:
            self.repository.add(city)
        except (Exception):
            raise ValueError("Город c таким ID уже существует.")
        return city

    def update(self, updated_city: City) -> City:
        try:
            self.repository.update(updated_city)
        except (Exception):
            raise ValueError("Город не найден.")
        
        return updated_city

    def delete(self, city_id: int) -> None:
        try:
            self.repository.delete(city_id)
        except (Exception):
            raise ValueError("Город не найден.")
