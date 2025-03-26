from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.user import User
from services.user_service import AuthService
from services.user_service import UserRepository
from services.user_service import UserService


def test_service_should_registrate_user() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")
    with patch.object(UserRepository, "add", return_value=user, create=True) as mock_method:
        repository = UserRepository()
        user_service = AuthService(repository)
        user_service.registrate(user)
        mock_method.assert_called_once_with(user)


def test_service_should_successfull_delete_existed_user() -> None:
    with patch.object(UserRepository, "delete", return_value=None, create=True) as mock_method:
        repository = UserRepository()
        user_service = UserService(repository)
        user_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_user() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    user_service = UserService(repository)
    with pytest.raises(ValueError):
        user_service.delete(123)


def test_should_succesfull_get_existed_user_by_id() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")

    with patch.object(UserRepository, "get", return_value=user, create=True) as mock_method:
        repository = UserRepository()
        user_service = UserService(repository)
        user_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_service_should_throw_exception_at_get_not_existed_user() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    user_service = UserService(repository)
    with pytest.raises(ValueError):
        user_service.get_by_id(123)


def test_should_succesfull_update_existed_user_by_id() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")

    with patch.object(UserRepository, "update", return_value=user, create=True) as mock_method:
        repository = UserRepository()
        user_service = UserService(repository)
        user_service.update(user)
        mock_method.assert_called_once_with(user)


def test_service_should_throw_exception_at_update_not_existed_user() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")
    repository = Mock(**{"update.side_effect": ValueError})
    user_service = UserService(repository)
    with pytest.raises(ValueError):
        user_service.update(user)


def test_should_succesfull_login_existed_user_with_right_password() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")

    with patch.object(UserRepository, "get_by_login", return_value=user, create=True) as mock_method:
        repository = UserRepository()
        user_auth = AuthService(repository)
        answer = user_auth.login("proGsa", "1234D!f333")
        assert answer
        mock_method.assert_called_once_with("proGsa")


def test_should_succesfull_login_existed_user_with_wrong_password() -> None:
    user = User(
        user_id=1, 
        fio="Лобач Анастасия Олеговна",
        number_passport="1234567890", 
        phone_number="89261111111", 
        email="nl@ii.info", 
        login="proGsa", 
        password="1234D!f333")

    with patch.object(UserRepository, "get_by_login", return_value=user, create=True) as mock_method:
        repository = UserRepository()
        user_auth = AuthService(repository)
        answer = user_auth.login("proGsa", "1111")
        assert not answer
        mock_method.assert_called_once_with("proGsa")


def test_should_succesfull_login_not_existed_user() -> None:
    with patch.object(UserRepository, "get_by_login", return_value=None, create=True) as mock_method:
        repository = UserRepository()
        user_auth = AuthService(repository)
        answer = user_auth.login("proGsa", "1111")
        assert not answer
        mock_method.assert_called_once_with("proGsa")
