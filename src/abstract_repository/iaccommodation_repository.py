from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.accommodation import Accommodation


class IAccommodationRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[Accommodation]]:
        pass

    @abstractmethod
    def get_by_id(self, accommodation_id: int) -> Coroutine[Any, Any, Accommodation | None]:
        pass

    @abstractmethod
    def add(self, accommodation: Accommodation) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_accommodation: Accommodation) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, accommodation_id: int) -> Coroutine[Any, Any, None]:
        pass
