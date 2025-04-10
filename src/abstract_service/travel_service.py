from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.travel import Travel


Travel.model_rebuild()


class ITravelService(ABC):
    @abstractmethod
    async def get_by_id(self, travel_id: int) -> Travel | None:
        pass
    
    @abstractmethod
    async def get_all_travels(self) -> list[Travel]:
        pass

    @abstractmethod
    async def add(self, travel: Travel) -> Travel:
        pass

    @abstractmethod
    async def update(self, update_travel: Travel) -> Travel:
        pass

    @abstractmethod
    async def delete(self, travel_id: int) -> None:
        pass

