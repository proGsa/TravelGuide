from __future__ import annotations

from abc import ABC

from pydantic import BaseModel
from pydantic import EmailStr


class IUser(BaseModel, ABC):
    user_id: int
    fio: str
    number_passport: str
    phone_number: str
    email: EmailStr
    login: str
    password: str

