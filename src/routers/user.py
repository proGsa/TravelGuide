from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


user_router = APIRouter()

templates = Jinja2Templates(directory="templates")

get_sl_dep = Depends(get_service_locator)


@user_router.post("/register")
async def register_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().registrate(request)


@user_router.post("/login")
async def login_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().login(request)


@user_router.post("/profile")
async def get_user_profile(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().get_user_profile(request)


@user_router.get("/user.html", response_class=HTMLResponse)
async def get_all_users(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    users_data = await service_locator.get_user_contr().get_all_users()
    users = users_data.get("users", []) 
    return templates.TemplateResponse("user.html", {"request": request, "users": users})


@user_router.delete("/")
async def delete_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().delete_user(request)