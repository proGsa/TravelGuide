from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_list(self) -> list[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def add(self, user: User) -> None:
        pass

    @abstractmethod
    def update(self, update_user: User) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass