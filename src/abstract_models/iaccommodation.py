from __future__ import annotations

from abc import ABC
from datetime import datetime

from pydantic import BaseModel


class IAccommodation(BaseModel, ABC):
    accommodation_id: int
    duration: str
    location: str
    a_type: str
    datetime: datetime 