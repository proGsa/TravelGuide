from __future__ import annotations

from abc import ABC

from pydantic import BaseModel
from pydantic import Field

from models.city import City


class IDirectoryRoute(BaseModel, ABC):
    d_route_id: int
    type_transport: str
    cost: int
    distance: int
    departure_city: City | None = Field(default=None, description="Город, откуда начинается маршрут")
    destination_city: City | None = Field(default=None, description="Город, куда направляется маршрут")
