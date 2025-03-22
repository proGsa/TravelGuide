from __future__ import annotations

import re

from typing import ClassVar

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator


class User(BaseModel):
    MAX_FIO_LENGTH: ClassVar[int] = 100
    MAX_LOGIN_LENGTH: ClassVar[int] = 40
    MIN_PASSWORD_LENGTH: ClassVar[int] = 8
    PASSPORT_LENGTH: ClassVar[int] = 10

    user_id: int
    fio: str
    number_passport: str
    phone_number: str
    email: EmailStr
    login: str
    password: str

    @field_validator("user_id")
    @classmethod
    def validate_check_user_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("user_id должен быть положительным числом")
        return value

    @field_validator("fio")
    @classmethod
    def validate_check_fio_length(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError("fio должно быть длиннее")
        if len(value) > cls.MAX_FIO_LENGTH:
            raise ValueError("fio должно быть короче")
        return value

    @field_validator("login")
    @classmethod
    def validate_check_login_length(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError("login должен быть длиннее")
        if len(value) > cls.MAX_LOGIN_LENGTH:
            raise ValueError("login должен быть короче")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.fullmatch(r"8\d{10}", v):
            raise ValueError("Номер телефона должен содержать 11 цифр и первая цифра -- 8")
        return v

    @field_validator("number_passport")
    @classmethod
    def validate_passport(cls, v: str) -> str:
        if len(v) < cls.PASSPORT_LENGTH:
            raise ValueError("Номер паспорта должен содержать 10 цифр")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError("Пароль должен содержать не менее 8 символов")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[\W_]", v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return v
