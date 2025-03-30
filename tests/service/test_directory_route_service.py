from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.directory_route import DirectoryRoute
from services.directory_route_service import DirectoryRouteRepository
from services.directory_route_service import DirectoryRouteService


def test_service_should_successfull_delete_existed_d_route() -> None:
    with patch.object(DirectoryRouteRepository, "delete", return_value=None, create=True) as mock_method:
        repository = DirectoryRouteRepository()
        d_route_service = DirectoryRouteService(repository)
        d_route_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_d_route() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    d_route_service = DirectoryRouteService(repository)
    with pytest.raises(ValueError):
        d_route_service.delete(123)


def test_should_succesfull_get_existed_d_route_by_id() -> None:
    d_route = DirectoryRoute(
        d_route_id=1, 
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None
    )
    with patch.object(DirectoryRouteRepository, "get", return_value=d_route, create=True) as mock_method:
        repository = DirectoryRouteRepository()
        d_route_service = DirectoryRouteService(repository)
        d_route_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_service_should_throw_exception_at_get_not_existed_d_route() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    d_route_service = DirectoryRouteService(repository)
    with pytest.raises(ValueError):
        d_route_service.get_by_id(123)


def test_should_succesfull_update_existed_d_route_by_id() -> None:
    d_route = DirectoryRoute(
        d_route_id=1, 
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None
    )
    with patch.object(DirectoryRouteRepository, "update", return_value=d_route, create=True) as mock_method:
        repository = DirectoryRouteRepository()
        d_route_service = DirectoryRouteService(repository)
        d_route_service.update(d_route)
        mock_method.assert_called_once_with(d_route)


def test_service_should_throw_exception_at_update_not_existed_d_route() -> None:
    d_route = DirectoryRoute(
        d_route_id=1, 
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None
    )
    repository = Mock(**{"update.side_effect": ValueError})
    d_route_service = DirectoryRouteService(repository)
    with pytest.raises(ValueError):
        d_route_service.update(d_route)
