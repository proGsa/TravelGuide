from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


entertainment_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@entertainment_router.post("/api/entertainments", response_class=HTMLResponse)
async def create_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    await service_locator.get_ent_contr().create_new_entertainment(request)
    return templates.TemplateResponse("entertainment.html", {"request": request})


@entertainment_router.get("/entertainment.html", response_class=HTMLResponse)
async def get_all_entertainments(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    entertainment_list = await service_locator.get_ent_contr().get_all_entertainment()
    entertainments = entertainment_list.get("entertainments", []) 
    for e in entertainments:
        e['event_time'] = datetime.fromisoformat(e['event_time'])
    return templates.TemplateResponse("entertainment.html", {"request": request, "entertainments": entertainments})


@entertainment_router.get("/{entertainment_id}")
async def get_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_ent_contr().get_entertainment_details(request)
    if result is None:
        return {"error": "Entertainment not found"}
    return result


@entertainment_router.put("/api/entertainments/{entertainment_id}")
async def update_entertainment(entertainment_id: int, request: Request, 
                                service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    await service_locator.get_ent_contr().update_entertainment(entertainment_id, request)
    return templates.TemplateResponse("entertainment.html", {"request": request})


@entertainment_router.post("/entertainment/delete/{entertainment_id}", response_class=HTMLResponse)
async def delete_entertainment(entertainment_id: int, request: Request,
                                service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    await service_locator.get_ent_contr().delete_entertainment(entertainment_id)
    return RedirectResponse(url="/entertainment.html", status_code=303)

