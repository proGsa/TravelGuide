from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.accommodation import Accommodation


class IAccommodationRepository(ABC):
    @abstractmethod
    def get_list(self) -> list[Accommodation]:
        pass

    @abstractmethod
    def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        pass

    @abstractmethod
    def add(self, accommodation: Accommodation) -> None:
        pass

    @abstractmethod
    def update(self, update_accommodation: Accommodation) -> None:
        pass

    @abstractmethod
    def delete(self, accommodation_id: int) -> None:
        pass
