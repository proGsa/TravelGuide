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


accommodation_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@accommodation_router.post("/api/accommodations", response_class=HTMLResponse)
async def create_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    await service_locator.get_acc_contr().create_new_accommodation(request)
    return templates.TemplateResponse("accommodation.html", {"request": request})


@accommodation_router.get("/accommodation.html", response_class=HTMLResponse)
async def get_all_accommodations(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    accommodation_list = await service_locator.get_acc_contr().get_all_accommodation()
    accommodations = accommodation_list.get("accommodations", []) 
    for a in accommodations:
        a['check_in'] = datetime.fromisoformat(a['check_in'])
        a['check_out'] = datetime.fromisoformat(a['check_out'])
    return templates.TemplateResponse("accommodation.html", {"request": request, "accommodations": accommodations})


@accommodation_router.get("/accommodation.html")
async def get_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    acc = await service_locator.get_acc_contr().get_accommodation_details(request)
    if acc is None:
        return {"error": "Accommodation not found"}
    return acc


@accommodation_router.put("/api/accommodations/{accommodation_id}", response_class=HTMLResponse)
async def update_accommodation(accommodation_id: int, request: Request, 
                                service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    await service_locator.get_acc_contr().update_accommodation(accommodation_id, request)
    return templates.TemplateResponse("accommodation.html", {"request": request})


@accommodation_router.post("/accommodation/delete/{accommodation_id}", response_class=HTMLResponse)
async def delete_accommodation(accommodation_id: int, service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    await service_locator.get_acc_contr().delete_accommodation(accommodation_id)
    return RedirectResponse(url="/accommodation.html", status_code=303)