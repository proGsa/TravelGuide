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
async def create_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_acc_contr().create_new_accommodation(request)
    return {"status": "created"}


@router.get("/{accommodation_id}")
async def get_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    acc = await service_locator.get_acc_contr().get_accommodation_details(request)
    if acc is None:
        return {"error": "Accommodation not found"}
    return acc


@router.get("/")
async def get_all_accommodations(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        accommodation_list = await service_locator.get_acc_contr().get_all_accommodation()
        return {"accommodations": accommodation_list}
    except Exception as e:
        return {"error": "Error fetching accommodations", "details": str(e)}


@router.put("/")
async def update_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_acc_contr().update_accommodation(request)
    return {"status": "updated"}


@router.delete("/{accommodation_id}")
async def delete_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_acc_contr().delete_accommodation(request)
    return {"status": "deleted"}
