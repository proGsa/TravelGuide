from __future__ import annotations

from models.accommodation import Accommodation


class AccommodationRepository:
    def get(self, accommodation_id: int) -> Accommodation | None:
        pass

    def update(self, updated_accommodation: Accommodation) -> None:
        pass

    def delete(self, accommodation_id: int) -> None:
        pass

    def add(self, accommodation: Accommodation) -> None:
        pass


class AccommodationService:
    def __init__(self, repository: AccommodationRepository) -> None:
        self.repository = repository

    def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        return self.repository.get(accommodation_id)

    def add(self, accommodation: Accommodation) -> Accommodation:
        try:
            self.repository.add(accommodation)
        except (Exception):
            raise ValueError("Размещение c таким ID уже существует.")
        return accommodation

    def update(self, update_accommodation: Accommodation) -> Accommodation:
        try:
            self.repository.update(update_accommodation)
        except (Exception):
            raise ValueError("Размещение не найдено.")
        
        return update_accommodation

    def delete(self, accommodation_id: int) -> None:
        try:
            self.repository.delete(accommodation_id)
        except (Exception):
            raise ValueError("Размещение не найдено.")


