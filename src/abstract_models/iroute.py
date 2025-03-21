from __future__ import annotations

from abc import ABC

from pydantic import BaseModel
from pydantic import Field

from models.directory_route import DirectoryRoute


class IRoute(BaseModel, ABC):
    route_id: int
    d_route: DirectoryRoute | None = Field(default=None, description="Справочник маршрутов")
    