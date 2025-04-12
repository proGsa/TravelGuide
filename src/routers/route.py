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
async def create_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_route_contr().create_new_route(request)
    return {"status": "created"}


@router.get("/{route_id}")
async def get_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_route_contr().get_route_details(request)
    if result is None:
        return {"error": "Route not found"}
    return {"route": result}


@router.put("/")
async def update_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_route_contr().update_route(request)
    return {"status": "updated"}


@router.delete("/{route_id}")
async def delete_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_route_contr().delete_route(request)
    return {"status": "deleted"}


@router.get("/")
async def get_all_route(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        route_list = await service_locator.get_route_contr().get_all_route()
        return {"routes": route_list}
    except Exception as e:
        return {"error": "Error fetching routes", "details": str(e)}


@router.put("/change-transport")
async def change_transport(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        await service_locator.get_route_contr().change_transport(request)
        return {"message": "Transport updated successfully"}
    except Exception as e:
        return {"error": "Error updating transport", "details": str(e)}


@router.delete("/delete-city")
async def delete_city_from_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        await service_locator.get_route_contr().delete_city_from_route(request)
        return {"message": "City deleted from route successfully"}
    except Exception as e:
        return {"error": "Error deleting city from route", "details": str(e)}


@router.post("/add-city")
async def add_new_city(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        await service_locator.get_route_contr().add_new_city(request)
        return {"message": "City added to route successfully"}
    except Exception as e:
        return {"error": "Error adding city to route", "details": str(e)}