from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationInfo
from pydantic import field_validator

from models.directory_route import DirectoryRoute
from models.travel import Travel


class Route(BaseModel):
    route_id: int
    d_route: DirectoryRoute | None = Field(default=None, description="Справочник маршрутов")
    travels: Travel | None = Field(default=None, description="Путешествие")
    start_time: datetime 
    end_time: datetime 

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

    @field_validator('end_time')
    @classmethod
    def check_datetime_order(cls, value: datetime, values: ValidationInfo) -> datetime:
        entry_time = values.data['start_time']
        if entry_time and value <= entry_time:
            raise ValueError('end_time должен быть позже start_time')
        return value

    @field_validator('travels')
    @classmethod
    def check_users(cls, value: Travel | None) -> Travel | None:
        if value is not None and not isinstance(value, Travel):
            raise ValueError('travels должен быть экземпляром Travel')
        return value