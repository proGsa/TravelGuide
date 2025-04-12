from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from service_locator import ServiceLocator
from service_locator import get_service_locator


router = APIRouter()

get_sl_dep = Depends(get_service_locator)


@router.post("/")
async def create_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_ent_contr().create_new_entertainment(request)
    return {"status": "created"}


@router.get("/")
async def get_all_entertainments(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        entertainment_list = await service_locator.get_ent_contr().get_all_entertainment()
        return {"entertainments": entertainment_list}
    except Exception as e:
        return {"error": "Error fetching entertainments", "details": str(e)}


@router.get("/{entertainment_id}")
async def get_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_ent_contr().get_entertainment_details(request)
    if result is None:
        return {"error": "Entertainment not found"}
    return result


@router.put("/")
async def update_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_ent_contr().update_entertainment(request)
    return {"status": "updated"}


@router.delete("/{entertainment_id}")
async def delete_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_ent_contr().delete_entertainment(request)
    return {"status": "deleted"}
