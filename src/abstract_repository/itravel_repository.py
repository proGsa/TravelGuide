from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.travel import Travel


class ITravelRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[Travel]]:
        pass

    @abstractmethod
    def get_by_id(self, travel_id: int) -> Coroutine[Any, Any, Travel | None]:
        pass

    @abstractmethod
    def add(self, travel: Travel) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_travel: Travel) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, travel_id: int) -> Coroutine[Any, Any, None]:
        pass
