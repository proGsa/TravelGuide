from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentRepository
from services.entertainment_service import EntertainmentService


def test_service_should_successfull_delete_existed_entertainment() -> None:
    with patch.object(EntertainmentRepository, "delete", return_value=None, create=True) as mock_method:
        repository = EntertainmentRepository()
        entertainment_service = EntertainmentService(repository)
        entertainment_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_entertainment() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    entertainment_service = EntertainmentService(repository)
    with pytest.raises(ValueError):
        entertainment_service.delete(123)
        

def test_should_succesfull_get_existed_entertainment_by_id() -> None:
    entertainment = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )

    with patch.object(EntertainmentRepository, "get", return_value=entertainment, create=True) as mock_method:
        repository = EntertainmentRepository()
        entertainment_service = EntertainmentService(repository)
        entertainment_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_service_should_throw_exception_at_get_not_existed_entertainment() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    entertainment_service = EntertainmentService(repository)
    with pytest.raises(ValueError):
        entertainment_service.get_by_id(123)


def test_should_succesfull_update_existed_entertainment_by_id() -> None:
    entertainment = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )

    with patch.object(EntertainmentRepository, "update", return_value=entertainment, create=True) as mock_method:
        repository = EntertainmentRepository()
        entertainment_service = EntertainmentService(repository)
        entertainment_service.update(entertainment)
        mock_method.assert_called_once_with(entertainment)


def test_service_should_throw_exception_at_update_not_existed_entertainment() -> None:
    entertainment = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )
    repository = Mock(**{"update.side_effect": ValueError})
    entertainment_service = EntertainmentService(repository)
    with pytest.raises(ValueError):
        entertainment_service.update(entertainment)
