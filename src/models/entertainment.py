from __future__ import annotations

import re

from datetime import datetime

from pydantic import BaseModel
from pydantic import field_validator


class Entertainment(BaseModel):
    entertainment_id: int
    duration: str
    address: str
    event_name: str
    event_time: datetime 

    @field_validator('entertainment_id')
    @classmethod
    def check_entertainment_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('entertainment_id должен быть положительным числом')
        return value
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: str) -> str:
        if not re.match(r'^\d+\s*(час|часа|часов)$', v):
            raise ValueError('Продолжительность должна быть в часах')
        return v

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v:
            raise ValueError('Address must not be empty')
        return v

    @field_validator('event_name')
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        allowed_types = {'Музей', 'Концерт', 'Выставка', 'Фестиваль', 'Достопримечательности', 'Прогулка'}
        if v not in allowed_types:
            raise ValueError(f'event_name должен быть одним из следующих: {", ".join(allowed_types)}')
        return v