from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel
from pydantic import ValidationInfo
from pydantic import field_validator


class Accommodation(BaseModel):
    MAX_ADDRESS_LENGTH: ClassVar[int] = 50
    MAX_NAME_LENGTH: ClassVar[int] = 100
    MAX_RATE: ClassVar[int] = 5

    accommodation_id: int
    price: int
    address: str
    name: str
    type: str
    rating: int
    check_in: datetime
    check_out: datetime 

    @field_validator('accommodation_id')
    @classmethod
    def check_accommodation_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('accommodation_id должен быть положительным числом')
        return value

    @field_validator('price')
    @classmethod
    def check_price_is_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('price должен быть положительным числом')
        return value

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed_types = {'Отель', 'Хостел', 'Аппартаменты', 'Квартира'}
        if v not in allowed_types:
            raise ValueError(f'type должен быть одним из следующих: {", ".join(allowed_types)}')
        return v

    @field_validator('name')
    @classmethod
    def validate_check_name_length(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError('name должно быть длиннее')
        if len(value) > cls.MAX_NAME_LENGTH:
            raise ValueError('name должно быть короче')
        return value

    @field_validator('address')
    @classmethod
    def validate_check_address_length(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError('address должно быть длиннее')
        if len(value) > cls.MAX_ADDRESS_LENGTH:
            raise ValueError('address должно быть короче')
        return value

    @field_validator('rating')
    @classmethod
    def check_rating_between_one_and_five(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('rate должен быть положительным числом')
        if value > cls.MAX_RATE:
            raise ValueError('rate не может быть больше 5')
        return value
        
    @field_validator('check_out')
    @classmethod
    def check_datetime_order(cls, value: datetime, values: ValidationInfo) -> datetime:
        check_in = values.data['check_in']
        if check_in and value <= check_in:
            raise ValueError('check_out должен быть позже entry_datetime')
        return value