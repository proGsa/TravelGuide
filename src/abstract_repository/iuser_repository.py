from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def add(self, user: User) -> None:
        pass

    @abstractmethod
    async def update(self, update_user: User) -> None:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass