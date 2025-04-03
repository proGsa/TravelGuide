from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.entertainment import Entertainment


class IEntertainmentRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[Entertainment]]:
        pass

    @abstractmethod
    def get_by_id(self, entertainment_id: int) -> Coroutine[Any, Any, Entertainment | None]:
        pass

    @abstractmethod
    def add(self, entertainment: Entertainment) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_entertainment: Entertainment) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, entertainment_id: int) -> Coroutine[Any, Any, None]:
        pass
