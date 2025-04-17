from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


travel_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@travel_router.post("/api/travels", response_class=HTMLResponse)
async def create_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    await service_locator.get_travel_contr().create_new_travel(request)
    return templates.TemplateResponse("travel.html", {"request": request})


@travel_router.get("/{travel_id}")
async def get_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_travel_contr().get_travel_details(request)
    if result is None:
        return {"error": "Travel not found"}
    return result


@travel_router.get("/travel.html")
async def get_all_travels(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    print("AAJDLAKDHASDç")
    travel_list = await service_locator.get_travel_contr().get_all_travels()
    travels = travel_list.get("travels", []) 
    user_id = travels[0].users.user_id if travels and travels[0].users else None

    entertainments = travel_list.get("travels.entertainments", [])
    accommodations = travel_list.get("travels.accommodations", [])
    return templates.TemplateResponse("travel.html", {"request": request, "travels": travels, "user_id": user_id,
            "entertainments": entertainments,
            "accommodations": accommodations })


@travel_router.put("/")
async def update_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().update_travel(request)
    return {"status": "updated"}


@travel_router.delete("/{travel_id}")
async def delete_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().delete_travel(request)
    return {"status": "deleted"}


@travel_router.put("/complete")
async def complete_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    await service_locator.get_travel_contr().complete_travel(request)
    return {"status": "completed"}


@travel_router.get("/archive")
async def check_archive_travels(service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_travel_contr().check_archive_travels()
        return {"travel": result}
    except Exception as e:
        return {"error": "Error check archive travel", "details": str(e)}


@travel_router.post("/search")
async def search_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_travel_contr().search_travel(request)
        return {"travel": result}
    except Exception as e:
        return {"error": "Error searching travel", "details": str(e)}
