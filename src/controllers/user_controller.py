from __future__ import annotations

from typing import Any

from fastapi import Request

from models.user import User
from services.user_service import AuthService
from services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService, auth_service: AuthService) -> None:
        self.user_service = user_service
        self.auth_service = auth_service

    async def get_user_profile(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            user_id = data.get("id")
            if user_id is None:
                return {"message": "Missing 'id' in request"}
            user = await self.user_service.get_by_id(user_id)
            if user:
                return {
                    "user": {
                            "id": user.user_id,
                            "fio": user.fio,
                            "number_passport": user.number_passport,
                            "phone_number": user.phone_number,
                            "email": user.email,
                            "login": user.login,
                            "password": user.password,
                            "user_id": user.user_id,
                            "is_admin": user.is_admin
                        }
                }
            return {"message": "User not found"}
        except Exception as e:
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_users(self) -> dict[str, Any]:
        try:
            user_list = await self.user_service.get_list()
            return {
                "users": [
                    {
                        "id": u.user_id,
                        "fio": u.fio,
                        "number_passport": u.number_passport,
                        "phone_number": u.phone_number,
                        "email": u.email,
                        "login": u.login,
                        "password": u.password,
                        "user_id": u.user_id,
                        "is_admin": u.is_admin
                    }
                    for u in user_list
                ]
            }
        except Exception as e:
            return {"message": "Error fetching users", "error": str(e)}

    async def registrate(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            user = User(**data)
            registered_user = await self.auth_service.registrate(user)
            return {"message": "User registered successfully", "user_id": registered_user.user_id}
        except Exception as e:
            return {"message": "Error during registration", "error": str(e)}

    async def login(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            login = data.get("login")
            password = data.get("password")
            if not login or not password:
                return {"message": "Missing login or password"}

            success = await self.auth_service.login(login, password)
            if success:
                return {"message": "Login successful"}
            return {"message": "Invalid credentials"}
        except Exception as e:
            return {"message": "Error during login", "error": str(e)}
    
    async def delete_user(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            user_id = data.get("id")
            if user_id is None:
                return {"message": "Missing 'id' in request"}
            await self.user_service.delete(user_id)
            return {"message": "User deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting user", "error": str(e)}

