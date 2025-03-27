from __future__ import annotations

from abstract_service.travel_service import ITravelService
from models.travel import Travel


Travel.model_rebuild()


class TravelRepository:
    def get(self, travel_id: int) -> Travel | None:
        pass

    def update(self, updated_travel: Travel) -> None:
        pass

    def delete(self, travel_id: int) -> None:
        pass

    def add(self, travel: Travel) -> None:
        pass

    @staticmethod
    def values() -> list[Travel]:
        return []


class TravelService(ITravelService):
    def __init__(self, repository: TravelRepository) -> None:
        self.repository = repository

    def get_by_id(self, travel_id: int) -> Travel | None:
        return self.repository.get(travel_id)

    def get_all_travels(self) -> list[Travel]:
        return list(self.repository.values()) 

    def add(self, travel: Travel) -> Travel:
        try:
            self.repository.add(travel)
        except (Exception):
            raise ValueError("Путешествие c таким ID уже существует.")
        return travel

    def update(self, update_travel: Travel) -> Travel:
        try:
            self.repository.update(update_travel)
        except (Exception):
            raise ValueError("Путешествие не найдено.")
        return update_travel

    def delete(self, travel_id: int) -> None:
        try:
            self.repository.delete(travel_id)
        except (Exception):
            raise ValueError("Путешествие не найдено.")

