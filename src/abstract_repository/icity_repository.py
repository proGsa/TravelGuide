from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.city import City


class ICityRepository(ABC):
    @abstractmethod
    def get_list(self) -> list[City]:
        pass

    @abstractmethod
    def get_by_id(self, city_id: int) -> City | None:
        pass

    @abstractmethod
    def add(self, city: City) -> None:
        pass

    @abstractmethod
    def update(self, update_city: City) -> None:
        pass

    @abstractmethod
    def delete(self, city_id: int) -> None:
        pass
