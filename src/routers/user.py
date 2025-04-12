from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from service_locator import ServiceLocator
from service_locator import get_service_locator


router = APIRouter()


get_sl_dep = Depends(get_service_locator)


@router.post("/register")
async def register_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().registrate(request)


@router.post("/login")
async def login_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().login(request)


@router.post("/profile")
async def get_user_profile(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().get_user_profile(request)


@router.get("/")
async def get_all_users(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().get_all_users()


@router.delete("/")
async def delete_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_user_contr().delete_user(request)