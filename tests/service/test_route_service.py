from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.route import Route
from services.route_service import RouteRepository
from services.route_service import RouteService


def test_service_should_successfull_delete_existed_route() -> None:
    with patch.object(RouteRepository, "delete", return_value=None, create=True) as mock_method:
        repository = RouteRepository()
        route_service = RouteService(repository)
        route_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_route() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    route_service = RouteService(repository)
    with pytest.raises(ValueError):
        route_service.delete(123)


def test_should_succesfull_get_existed_route_by_id() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 3, 26, 10, 24, 00), 
                                                            end_time=datetime(2025, 3, 28, 18, 0, 0))

    with patch.object(RouteRepository, "get", return_value=route, create=True) as mock_method:
        repository = RouteRepository()
        route_service = RouteService(repository)
        route_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_should_succesfull_get_routes() -> None:
    routes = [
        Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 3, 26, 10, 24, 00), 
                                                        end_time=datetime(2025, 3, 28, 18, 0, 0)),
        Route(route_id=2, d_route=None, travels=None, start_time=datetime(2025, 4, 6, 10, 24, 00), 
                                                        end_time=datetime(2025, 4, 8, 18, 0, 0))
    ]
    with patch.object(RouteRepository, "values", return_value=routes, create=True) as mock_method:
        repository = RouteRepository()
        route_service = RouteService(repository)
        route_service.get_all_routes()
        mock_method.assert_called_once()


def test_service_should_throw_exception_at_get_not_existed_route() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    route_service = RouteService(repository)
    with pytest.raises(ValueError):
        route_service.get_by_id(123)


def test_should_succesfull_update_existed_route_by_id() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 3, 26, 10, 24, 00), 
                                                            end_time=datetime(2025, 3, 28, 18, 0, 0))
    with patch.object(RouteRepository, "update", return_value=route, create=True) as mock_method:
        repository = RouteRepository()
        route_service = RouteService(repository)
        route_service.update(route)
        mock_method.assert_called_once_with(route)


def test_service_should_throw_exception_at_update_not_existed_route() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 3, 26, 10, 24, 00), 
                                                            end_time=datetime(2025, 3, 28, 18, 0, 0))
    repository = Mock(**{"update.side_effect": ValueError})
    route_service = RouteService(repository)
    with pytest.raises(ValueError):
        route_service.update(route)
