from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.user import User


class IUserService(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def update(self, updated_user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass
        

class IAuthService(ABC):
    @abstractmethod
    def registrate(self, user: User) -> User:
        pass

    @abstractmethod
    def login(self, login: str, password: str) -> bool:
        pass
