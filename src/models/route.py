from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from models.directory_route import DirectoryRoute


class Route(BaseModel):
    route_id: int
    d_route: DirectoryRoute | None = Field(default=None, description="Справочник маршрутов")
    
    @field_validator('route_id')
    @classmethod
    def check_route_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('route_id должен быть положительным числом')
        return value

    @field_validator('d_route')
    @classmethod
    def check_d_route(cls, value: DirectoryRoute | None) -> DirectoryRoute | None:
        if value is not None and not isinstance(value, DirectoryRoute):
            raise ValueError('d_route должен быть экземпляром DirectoryRoute')
        return value