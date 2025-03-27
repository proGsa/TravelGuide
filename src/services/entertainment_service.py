from __future__ import annotations

from abstract_service.entertainment_service import IEntertainmentService
from models.entertainment import Entertainment


class EntertainmentRepository:
    def get(self, entertainment_id: int) -> Entertainment | None:
        pass

    def update(self, updated_entertainment: Entertainment) -> None:
        pass

    def delete(self, entertainment_id: int) -> None:
        pass

    def add(self, entertainment: Entertainment) -> None:
        pass


class EntertainmentService(IEntertainmentService):
    def __init__(self, repository: EntertainmentRepository) -> None:
        self.repository = repository

    def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        return self.repository.get(entertainment_id)

    def add(self, entertainment: Entertainment) -> Entertainment:
        try:
            self.repository.add(entertainment)
        except (Exception):
            raise ValueError("Развлечение c таким ID уже существует.")
        return entertainment

    def update(self, update_entertainment: Entertainment) -> Entertainment:
        try:
            self.repository.update(update_entertainment)
        except (Exception):
            raise ValueError("Развлечение не найдено.")
        return update_entertainment

    def delete(self, entertainment_id: int) -> None:
        try:
            self.repository.delete(entertainment_id)
        except (Exception):
            raise ValueError("Развлечение не найдено.")


