from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import ValidationInfo
from pydantic import field_validator

from abstract_models.ientertainment import IEntertainment


class Entertainment(IEntertainment):
    MAX_ADDRESS_LENGTH: ClassVar[int] = 50
    MAX_NAME_LENGTH: ClassVar[int] = 100
    MAX_RATE: ClassVar[int] = 5

    @field_validator('entertainment_id')
    @classmethod
    def check_entertainment_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('entertainment_id должен быть положительным числом')
        return value

    @field_validator('cost')
    @classmethod
    def check_cost_is_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('cost должен быть положительным числом')
        return value

    @field_validator('e_type')
    @classmethod
    def validate_e_type(cls, v: str) -> str:
        allowed_types = {'Отель', 'Хостел', 'Аппартаменты', 'Квартира'}
        if v not in allowed_types:
            raise ValueError(f'e_type должен быть одним из следующих: {", ".join(allowed_types)}')
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
        
    @field_validator('departure_datetime')
    @classmethod
    def check_datetime_order(cls, value: datetime, values: ValidationInfo) -> datetime:
        entry_time = values.data['entry_datetime']
        if entry_time and value <= entry_time:
            raise ValueError('departure_datetime должен быть позже entry_datetime')
        return value