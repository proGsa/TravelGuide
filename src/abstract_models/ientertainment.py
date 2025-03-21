from __future__ import annotations

from abc import ABC
from datetime import datetime

from pydantic import BaseModel


class IEntertainment(BaseModel, ABC):
    entertainment_id: int
    cost: int
    address: str
    name: str
    e_type: str
    rating: int
    entry_datetime: datetime
    departure_datetime: datetime 