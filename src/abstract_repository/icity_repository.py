from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.city import City


class ICityRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[City]]:
        pass

    @abstractmethod
    def get_by_id(self, city_id: int) -> Coroutine[Any, Any, City | None]:
        pass

    @abstractmethod
    def add(self, city: City) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_city: City) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, city_id: int) -> Coroutine[Any, Any, None]:
        pass
