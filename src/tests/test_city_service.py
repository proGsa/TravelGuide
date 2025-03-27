from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.city import City
from services.city_service import CityRepository
from services.city_service import CityService


def test_service_should_successfull_delete_existed_city() -> None:
    with patch.object(CityRepository, "delete", return_value=None, create=True) as mock_method:
        repository = CityRepository()
        city_service = CityService(repository)
        city_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_city() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    city_service = CityService(repository)
    with pytest.raises(ValueError):
        city_service.delete(123)


def test_should_succesfull_get_cities() -> None:
    cities = [
        City(city_id=1, name="Москва"),
        City(city_id=2, name="Казань")
    ]
    with patch.object(CityRepository, "values", return_value=cities, create=True) as mock_method:
        repository = CityRepository()
        city_service = CityService(repository)
        city_service.get_all_cities()
        mock_method.assert_called_once()


def test_should_succesfull_get_existed_city_by_id() -> None:
    city = City(city_id=1, name="Москва")

    with patch.object(CityRepository, "get", return_value=city, create=True) as mock_method:
        repository = CityRepository()
        city_service = CityService(repository)
        city_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_service_should_throw_exception_at_get_not_existed_city() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    city_service = CityService(repository)
    with pytest.raises(ValueError):
        city_service.get_by_id(123)


def test_should_succesfull_update_existed_city_by_id() -> None:
    city = City(city_id=1, name="Москва")

    with patch.object(CityRepository, "update", return_value=city, create=True) as mock_method:
        repository = CityRepository()
        city_service = CityService(repository)
        city_service.update(city)
        mock_method.assert_called_once_with(city)


def test_service_should_throw_exception_at_update_not_existed_city() -> None:
    city = City(city_id=1, name="Москва")
    repository = Mock(**{"update.side_effect": ValueError})
    city_service = CityService(repository)
    with pytest.raises(ValueError):
        city_service.update(city)
