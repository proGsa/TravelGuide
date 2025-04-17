from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.accommodation import Accommodation
from services.accommodation_service import AccommodationRepository
from services.accommodation_service import AccommodationService


def test_service_should_successfull_delete_existed_accommodation() -> None:
    with patch.object(AccommodationRepository, "delete", return_value=None, create=True) as mock_method:
        repository = AccommodationRepository()
        accommodation_service = AccommodationService(repository)
        accommodation_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_accommodation() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    accommodation_service = AccommodationService(repository)
    with pytest.raises(ValueError):
        accommodation_service.delete(123)


def test_should_succesfull_get_existed_accommodation_by_id() -> None:
    accommodation = Accommodation(
        accommodation_id=1,
        price=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        type="Отель",
        rating=5,
        check_in=datetime(2023, 10, 10, 10, 0, 0),
        check_out=datetime(2023, 10, 10, 18, 0, 0)
    )

    with patch.object(AccommodationRepository, "get_by_id", return_value=accommodation, create=True) as mock_method:
        repository = AccommodationRepository()
        accommodation_service = AccommodationService(repository)
        accommodation_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_service_should_throw_exception_at_get_not_existed_accommodation() -> None:
    repository = Mock(**{"get_by_id.side_effect": ValueError})
    accommodation_service = AccommodationService(repository)
    with pytest.raises(ValueError):
        accommodation_service.get_by_id(123)


def test_should_succesfull_update_existed_accommodation_by_id() -> None:
    accommodation = Accommodation(
        accommodation_id=1,
        price=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        type="Отель",
        rating=5,
        check_in=datetime(2023, 10, 10, 10, 0, 0),
        check_out=datetime(2023, 10, 10, 18, 0, 0)
    )

    with patch.object(AccommodationRepository, "update", return_value=accommodation, create=True) as mock_method:
        repository = AccommodationRepository()
        accommodation_service = AccommodationService(repository)
        accommodation_service.update(accommodation)
        mock_method.assert_called_once_with(accommodation)


def test_service_should_throw_exception_at_update_not_existed_accommodation() -> None:
    accommodation = Accommodation(
        accommodation_id=1,
        price=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        type="Отель",
        rating=5,
        check_in=datetime(2023, 10, 10, 10, 0, 0),
        check_out=datetime(2023, 10, 10, 18, 0, 0)
    )
    repository = Mock(**{"update.side_effect": ValueError})
    accommodation_service = AccommodationService(repository)
    with pytest.raises(ValueError):
        accommodation_service.update(accommodation)
