from __future__ import annotations

from models.user import User
from services.user_service import AuthService
from services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService, auth_service: AuthService) -> None:
        self.user_service = user_service
        self.auth_service = auth_service

    async def get_user_profile(self, user_id: int) -> User | None:
        try:
            return await self.user_service.get_by_id(user_id)
        except Exception as e:
            print(f"Ошибка при получении данных пользователя: {e}s")
        return None

    async def registrate(self, user: User) -> User | None:
        try:
            return await self.auth_service.registrate(user)
        except Exception as e:
            print(f"Ошибка при получении данных размещения: {e}s")
        return None

    async def login(self, login: str, password: str) -> bool:
        try:
            return await self.auth_service.login(login, password)
        except Exception as e:
            print(f"Ошибка при получении данных размещения: {e}s")
        return False
    
    async def delete_user(self, user_id: int) -> None:
        try:
            await self.user_service.delete(user_id)
        except Exception as e:
            print(f"Ошибка при обновлении размещения: {e}s")
    