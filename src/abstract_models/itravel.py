from __future__ import annotations

from abc import ABC

from pydantic import BaseModel
from pydantic import Field

from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.route import Route
from models.user import User


class ITravel(BaseModel, ABC):
    travel_id: int
    status: str
    route: Route | None = Field(default=None, description="ID маршрута")
    users: User | None = Field(default=None, description="ID пользователя")
    entertainments: list[Entertainment] = Field(default_factory=list, description="Список развлечения")
    accommodations: list[Accommodation] = Field(default_factory=list, description="Список размещения")