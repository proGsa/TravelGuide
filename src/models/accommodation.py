from __future__ import annotations

import re

from datetime import datetime

from pydantic import BaseModel
from pydantic import field_validator


class Accommodation(BaseModel):
    accommodation_id: int
    duration: str
    location: str
    a_type: str
    datetime: datetime 

    @field_validator('accommodation_id')
    @classmethod
    def check_accommodation_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('accommodation_id должен быть положительным числом')
        return value
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: str) -> str:
        if not re.match(r'^\d+\s*(час|часа|часов)$', v):
            raise ValueError('Продолжительность должна быть в часах')
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v:
            raise ValueError('Location must not be empty')
        return v

    @field_validator('a_type')
    @classmethod
    def validate_a_type(cls, v: str) -> str:
        allowed_types = {'Музей', 'Концерт', 'Выставка', 'Фестиваль', 'Достопримечательности', 'Прогулка'}
        if v not in allowed_types:
            raise ValueError(f'a_type должен быть одним из следующих: {", ".join(allowed_types)}')
        return v