from __future__ import annotations

import asyncio

from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from controllers.accommodation_controller import AccommodationController
from controllers.entertainment_controller import EntertainmentController
from controllers.route_controller import RouteController
from controllers.travel_controller import TravelController
from controllers.user_controller import UserController
from repository.accommodation_repository import AccommodationRepository
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.route_repository import RouteRepository
from repository.travel_repository import TravelRepository
from repository.user_repository import UserRepository
from services.accommodation_service import AccommodationService
from services.city_service import CityService
from services.directory_route_service import DirectoryRouteService
from services.entertainment_service import EntertainmentService
from services.route_service import RouteService
from services.travel_service import TravelService
from services.user_service import AuthService
from services.user_service import UserService


@dataclass
class Repositories:
    def __init__(self, acc_repo: AccommodationRepository, city_repo: CityRepository, 
            d_route_repo: DirectoryRouteRepository, ent_repo: EntertainmentRepository, 
            route_repo: RouteRepository, travel_repo: TravelRepository, user_repo: UserRepository):
        self.acc_repo = acc_repo
        self.city_repo = city_repo
        self.d_route_repo = d_route_repo
        self.ent_repo = ent_repo
        self.route_repo = route_repo
        self.travel_repo = travel_repo
        self.user_repo = user_repo
        

@dataclass
class Services:
    def __init__(self, acc_serv: AccommodationService, city_serv: CityService, 
            d_route_serv: DirectoryRouteService, ent_serv: EntertainmentService, 
            route_serv: RouteService, travel_serv: TravelService, user_serv: UserService, auth_serv: AuthService):
        self.acc_serv = acc_serv
        self.city_serv = city_serv
        self.d_route_serv = d_route_serv
        self.ent_serv = ent_serv
        self.route_serv = route_serv
        self.travel_serv = travel_serv
        self.user_serv = user_serv
        self.auth_serv = auth_serv


@dataclass
class Controllers:
    def __init__(self, acc_contr: AccommodationController, route_contr: RouteController, 
            ent_contr: EntertainmentController, travel_contr: TravelController, user_contr: UserController):
        self.acc_contr = acc_contr
        self.route_contr = route_contr
        self.ent_contr = ent_contr
        self.travel_contr = travel_contr
        self.user_contr = user_contr


class ServiceLocator:
    def __init__(self, repositories: Repositories, services: Services, controllers: Controllers):
        self.repositories = repositories
        self.services = services
        self.controllers = controllers

    def get_acc_repo(self) -> AccommodationRepository:
        return self.repositories.acc_repo

    def get_city_repo(self) -> CityRepository:
        return self.repositories.city_repo

    def get_d_route_repo(self) -> DirectoryRouteRepository:
        return self.repositories.d_route_repo

    def get_ent_repo(self) -> EntertainmentRepository:
        return self.repositories.ent_repo

    def get_route_repo(self) -> RouteRepository:
        return self.repositories.route_repo

    def get_travel_repo(self) -> TravelRepository:
        return self.repositories.travel_repo

    def get_user_repo(self) -> UserRepository:
        return self.repositories.user_repo

    def get_acc_serv(self) -> AccommodationService:
        return self.services.acc_serv

    def get_city_serv(self) -> CityService:
        return self.services.city_serv

    def get_d_route_serv(self) -> DirectoryRouteService:
        return self.services.d_route_serv

    def get_ent_serv(self) -> EntertainmentService:
        return self.services.ent_serv

    def get_route_serv(self) -> RouteService:
        return self.services.route_serv

    def get_travel_serv(self) -> TravelService:
        return self.services.travel_serv

    def get_user_serv(self) -> UserService:
        return self.services.user_serv

    def get_auth_serv(self) -> AuthService:
        return self.services.auth_serv

    def get_acc_contr(self) -> AccommodationController:
        return self.controllers.acc_contr

    def get_route_contr(self) -> RouteController:
        return self.controllers.route_contr

    def get_ent_contr(self) -> EntertainmentController:
        return self.controllers.ent_contr

    def get_travel_contr(self) -> TravelController:
        return self.controllers.travel_contr

    def get_user_contr(self) -> UserController:
        return self.controllers.user_contr


async def get_sessionmaker(max_retries: int = 5, delay: int = 2) -> Any:
    engine = create_async_engine(
        "postgresql+asyncpg://nastya@localhost:5432/postgres",
        connect_args={
            "server_settings": {
                "search_path": "travel_db" 
            }
        },
        echo=True
    )
    
    for attempt in range(max_retries):
        try:
            return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        except OperationalError as e:
            print(f"Ошибка подключения к БД: {e}")
            if attempt < max_retries - 1:
                print(f"Повторная попытка подключения через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                print("Превышено максимальное количество попыток подключения.")
                raise
    return None


async def get_service_locator() -> ServiceLocator:
    async_session_maker = await get_sessionmaker()
    async with async_session_maker() as session:
        acc_repo = AccommodationRepository(session)
        city_repo = CityRepository(session)
        d_route_repo = DirectoryRouteRepository(session, city_repo)
        ent_repo = EntertainmentRepository(session)
        user_repo = UserRepository(session)
        travel_repo = TravelRepository(session, user_repo, ent_repo, acc_repo)
        route_repo = RouteRepository(session, d_route_repo, travel_repo)

        acc_serv = AccommodationService(acc_repo)
        city_serv = CityService(city_repo)
        d_route_serv = DirectoryRouteService(d_route_repo)
        ent_serv = EntertainmentService(ent_repo)
        route_serv = RouteService(route_repo)
        travel_serv = TravelService(travel_repo)
        user_serv = UserService(user_repo)
        auth_serv = AuthService(user_repo)
        
        acc_contr = AccommodationController(acc_serv)
        route_contr = RouteController(route_serv) 
        ent_contr = EntertainmentController(ent_serv)
        travel_contr = TravelController(travel_serv)
        user_contr = UserController(user_serv, auth_serv)

        repositories = Repositories(acc_repo, city_repo, d_route_repo, ent_repo, route_repo, travel_repo, user_repo)
        services = Services(acc_serv, city_serv, d_route_serv, ent_serv, route_serv, travel_serv, user_serv, auth_serv)
        controllers = Controllers(acc_contr, route_contr, ent_contr, travel_contr, user_contr)
        
        return ServiceLocator(repositories, services, controllers)
    
    raise ValueError("Session was not provided.")