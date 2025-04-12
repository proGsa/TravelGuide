from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from services.travel_service import TravelRepository
from services.travel_service import TravelService


def test_service_should_successfull_delete_existed_travel() -> None:
    with patch.object(TravelRepository, "delete", return_value=None, create=True) as mock_method:
        repository = TravelRepository()
        travel_service = TravelService(repository)
        travel_service.delete(123)
        mock_method.assert_called_once_with(123)


def test_service_should_throw_exception_at_delete_not_existed_travel() -> None:
    repository = Mock(**{"delete.side_effect": ValueError})
    travel_service = TravelService(repository)
    with pytest.raises(ValueError):
        travel_service.delete(123)


def test_should_succesfull_get_existed_travel_by_id() -> None:
    accommodation1 = Accommodation(
        accommodation_id=1,
        cost=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        e_type="Отель",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )

    accommodation2 = Accommodation(
        accommodation_id=1,
        cost=10000,
        address="Улица Гоголя, 15",
        name="Чайка",
        e_type="Хостел",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )
    entertainment1 = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )
    entertainment2 = Entertainment(
        entertainment_id=2, 
        duration="4 часа",
        location="дворцовая площадь", 
        a_type="Музей", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
    )

    travel = Travel(
        travel_id=1,
        status="В процессе",
        users=None,
        accommodations=[accommodation1, accommodation2],
        entertainments=[entertainment1, entertainment2]
    )

    with patch.object(TravelRepository, "get", return_value=travel, create=True) as mock_method:
        repository = TravelRepository()
        travel_service = TravelService(repository)
        travel_service.get_by_id(1)
        mock_method.assert_called_once_with(1)


def test_should_succesfull_get_travels() -> None:
    accommodation1 = Accommodation(
        accommodation_id=1,
        cost=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        e_type="Отель",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )

    accommodation2 = Accommodation(
        accommodation_id=1,
        cost=10000,
        address="Улица Гоголя, 15",
        name="Чайка",
        e_type="Хостел",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )
    entertainment1 = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )
    entertainment2 = Entertainment(
        entertainment_id=2, 
        duration="4 часа",
        location="дворцовая площадь", 
        a_type="Музей", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
    )

    travels = [
        Travel(
            travel_id=1,
            status="В процессе",
            users=None,
            accommodations=[accommodation1, accommodation2],
            entertainments=[entertainment1, entertainment2]
            ),
        Travel(
            travel_id=2,
            status="Завершен",
            users=None,
            accommodations=[accommodation1, accommodation2],
            entertainments=[entertainment1, entertainment2]
            )
    ]
    with patch.object(TravelRepository, "get_list", return_value=travels, create=True) as mock_method:
        repository = TravelRepository()
        travel_service = TravelService(repository)
        travel_service.get_all_travels()
        mock_method.assert_called_once()


def test_service_should_throw_exception_at_get_not_existed_travel() -> None:
    repository = Mock(**{"get.side_effect": ValueError})
    travel_service = TravelService(repository)
    with pytest.raises(ValueError):
        travel_service.get_by_id(123)


def test_should_succesfull_update_existed_travel_by_id() -> None:
    accommodation1 = Accommodation(
        accommodation_id=1,
        cost=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        e_type="Отель",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )

    accommodation2 = Accommodation(
        accommodation_id=1,
        cost=10000,
        address="Улица Гоголя, 15",
        name="Чайка",
        e_type="Хостел",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )
    entertainment1 = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0) 
        )
    entertainment2 = Entertainment(
        entertainment_id=2, 
        duration="4 часа",
        location="дворцовая площадь", 
        a_type="Музей", 
        datetime=datetime(2023, 10, 10, 10, 0, 0) 
    )

    travel = Travel(
        travel_id=1,
        status="В процессе",
        users=None,
        accommodations=[accommodation1, accommodation2],
        entertainments=[entertainment1, entertainment2]
    )

    with patch.object(TravelRepository, "update", return_value=travel, create=True) as mock_method:
        repository = TravelRepository()
        travel_service = TravelService(repository)
        travel_service.update(travel)
        mock_method.assert_called_once_with(travel)


def test_service_should_throw_exception_at_update_not_existed_travel() -> None:
    accommodation1 = Accommodation(
        accommodation_id=1,
        cost=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        e_type="Отель",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )

    accommodation2 = Accommodation(
        accommodation_id=1,
        cost=10000,
        address="Улица Гоголя, 15",
        name="Чайка",
        e_type="Хостел",
        rating=5,
        entry_datetime=datetime(2023, 10, 10, 10, 0, 0),
        departure_datetime=datetime(2023, 10, 10, 18, 0, 0)
    )
    entertainment1 = Entertainment(
        entertainment_id=1, 
        duration="4 часа",
        location="главная площадь", 
        a_type="Концерт", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
        )
    entertainment2 = Entertainment(
        entertainment_id=2, 
        duration="4 часа",
        location="дворцовая площадь", 
        a_type="Музей", 
        datetime=datetime(2023, 10, 10, 10, 0, 0)
    )

    travel = Travel(
        travel_id=1,
        status="В процессе",
        users=None,
        accommodations=[accommodation1, accommodation2],
        entertainments=[entertainment1, entertainment2]
    )

    repository = Mock(**{"update.side_effect": ValueError})
    travel_service = TravelService(repository)
    with pytest.raises(ValueError):
        travel_service.update(travel)
