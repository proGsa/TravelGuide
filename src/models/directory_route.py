from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from models.city import City


class DirectoryRoute(BaseModel):
    d_route_id: int
    type_transport: str
    cost: int
    distance: int
    departure_city: City | None = Field(default=None, description="Город, откуда начинается маршрут")
    destination_city: City | None = Field(default=None, description="Город, куда направляется маршрут")

    @field_validator('d_route_id')
    @classmethod
    def check_d_route_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('d_route_id должен быть положительным числом')
        return value

    @field_validator('cost')
    @classmethod
    def check_cost_is_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('cost должен быть положительным числом')
        return value

    @field_validator('type_transport')
    @classmethod
    def validate_type_transport(cls, v: str) -> str:
        allowed_types = {'Автобус', 'Самолет', 'Автомобиль', 'Паром', 'Поезд'}
        if v not in allowed_types:
            raise ValueError(f'e_type должен быть одним из следующих: {", ".join(allowed_types)}')
        return v
    
    @field_validator('distance')
    @classmethod
    def check_distance_is_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('distance должен быть положительным числом')
        return value

    @field_validator('departure_city')
    @classmethod
    def check_departure_city(cls, value: City | None) -> City | None:
        if value is not None and not isinstance(value, City):
            raise ValueError('departure_city должен быть экземпляром City')
        return value

    @field_validator('destination_city')
    @classmethod
    def check_destination_city(cls, value: City | None) -> City | None:
        if value is not None and not isinstance(value, City):
            raise ValueError('destination_city должен быть экземпляром City')
        return value