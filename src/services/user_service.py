from __future__ import annotations

from abstract_service.user_service import IAuthService
from abstract_service.user_service import IUserService
from models.user import User


class UserRepository:
    def get(self, user_id: int) -> User | None:
        pass

    def update(self, updated_user: User) -> None:
        pass

    def delete(self, user_id: int) -> None:
        pass

    def add(self, user: User) -> None:
        pass

    def get_by_login(self, login: str) -> User | None:
        pass


class UserService(IUserService):
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def get_by_id(self, user_id: int) -> User | None:
        return self.repository.get(user_id)

    def update(self, updated_user: User) -> User:
        try:
            self.repository.update(updated_user)
        except (Exception):
            raise ValueError("Пользователь не найден.")
        
        return updated_user

    def delete(self, user_id: int) -> None:
        try:
            self.repository.delete(user_id)
        except (Exception):
            raise ValueError("Пользователь не найден.")
        

class AuthService(IAuthService):
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def registrate(self, user: User) -> User:
        try:
            self.repository.add(user)
        except (Exception):
            raise ValueError("Пользователь c таким ID уже существует.")

        return user

    def login(self, login: str, password: str) -> bool:
        if user := self.repository.get_by_login(login):
            return user.password == password
        return False
