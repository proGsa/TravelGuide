from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.accommodation import Accommodation


class IAccommodationService(ABC):
    @abstractmethod
    def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        pass

    @abstractmethod
    def add(self, accommodation: Accommodation) -> Accommodation:
        pass

    @abstractmethod
    def update(self, update_accommodation: Accommodation) -> Accommodation:
        pass

    @abstractmethod
    def delete(self, accommodation_id: int) -> None:
        pass
