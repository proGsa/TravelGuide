from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.user import User


class IUserService(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def update(self, updated_user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass
        

class IAuthService(ABC):
    @abstractmethod
    async def registrate(self, user: User) -> User:
        pass

    @abstractmethod
    async def login(self, login: str, password: str) -> bool:
        pass
