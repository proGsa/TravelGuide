from __future__ import annotations

from abc import ABC

from pydantic import BaseModel


class ICity(BaseModel, ABC):
    city_id: int
    name: str