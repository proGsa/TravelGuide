from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.entertainment import Entertainment


class IEntertainmentRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[Entertainment]:
        pass

    @abstractmethod
    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        pass

    @abstractmethod
    async def add(self, entertainment: Entertainment) -> None:
        pass

    @abstractmethod
    async def update(self, update_entertainment: Entertainment) -> None:
        pass

    @abstractmethod
    async def delete(self, entertainment_id: int) -> None:
        pass
