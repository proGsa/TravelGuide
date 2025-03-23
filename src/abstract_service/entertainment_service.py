from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.entertainment import Entertainment


class IEntertainmentService(ABC):
    @abstractmethod
    def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        pass

    @abstractmethod
    def add(self, entertainment: Entertainment) -> Entertainment:
        pass

    @abstractmethod
    def update(self, update_entertainment: Entertainment) -> Entertainment:
        pass

    @abstractmethod
    def delete(self, entertainment_id: int) -> None:
        pass


