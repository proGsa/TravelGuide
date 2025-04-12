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
async def create_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().create_new_travel(request)
    return {"status": "created"}


@router.get("/{travel_id}")
async def get_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_travel_contr().get_travel_details(request)
    if result is None:
        return {"error": "Travel not found"}
    return result


@router.put("/")
async def update_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().update_travel(request)
    return {"status": "updated"}


@router.delete("/{travel_id}")
async def delete_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().delete_travel(request)
    return {"status": "deleted"}


@router.get("/all")
async def get_all_travels(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_travel_contr().get_all_travels()
        return {"travels": result}
    except Exception as e:
        return {"error": "Error fetching travels", "details": str(e)}


@router.put("/complete")
async def complete_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().complete_travel(request)
    return {"status": "completed"}


@router.get("/archive")
async def check_archive_travels(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_travel_contr().check_archive_travels()
        return {"travel": result}
    except Exception as e:
        return {"error": "Error check archive travel", "details": str(e)}


@router.post("/search")
async def search_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_travel_contr().search_travel(request)
        return {"travel": result}
    except Exception as e:
        return {"error": "Error searching travel", "details": str(e)}
