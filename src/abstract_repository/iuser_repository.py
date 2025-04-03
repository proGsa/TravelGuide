from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Coroutine

from models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_list(self) -> Coroutine[Any, Any, list[User]]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Coroutine[Any, Any, User | None]:
        pass

    @abstractmethod
    def add(self, user: User) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def update(self, update_user: User) -> Coroutine[Any, Any, None]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> Coroutine[Any, Any, None]:
        pass