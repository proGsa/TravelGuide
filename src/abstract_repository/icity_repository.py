from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.city import City


class ICityRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[City]:
        pass

    @abstractmethod
    async def get_by_id(self, city_id: int) -> City | None:
        pass

    @abstractmethod
    async def add(self, city: City) -> None:
        pass

    @abstractmethod
    async def update(self, update_city: City) -> None:
        pass

    @abstractmethod
    async def delete(self, city_id: int) -> None:
        pass
