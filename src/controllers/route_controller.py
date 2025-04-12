from __future__ import annotations

from typing import Any

from fastapi import Request

from models.route import Route
from services.route_service import RouteService


class RouteController:
    def __init__(self, route_service: RouteService) -> None:
        self.route_service = route_service

    async def create_new_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route = Route(**data)
            await self.route_service.add(route)
            return {"message": "Route created successfully"}
        except Exception as e:
            return {"message": "Error creating route", "error": str(e)}

    async def add_new_city(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_id = data.get("travel_id")
            new_city_id = data.get("new_city_id")
            from_city_id = data.get("from_city_id")
            to_city_id = data.get("to_city_id")

            if not travel_id or not new_city_id or not from_city_id or not to_city_id:
                return {"message": "Missing required fields in request"}

            await self.route_service.insert_city_between(travel_id, new_city_id, from_city_id, to_city_id)
            return {"message": "City added to route successfully"}
        except Exception as e:
            return {"message": "Error adding city to route", "error": str(e)}
       
    async def delete_city_from_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            city_id = data.get("id")
            if city_id is None:
                return {"message": "Missing 'id' in request"}
            await self.route_service.delete_city_from_route(city_id)
            return {"message": "Entertainment not found"}
        except Exception as e:
            return {"message": "Error delete city from route", "error": str(e)}
    
    async def update_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route = Route(**data)
            await self.route_service.update(route)
            return {"message": "Route updated successfully"}
        except Exception as e:
            return {"message": "Error updating route", "error": str(e)}
 
    async def change_transport(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route_id = data.get("route_id")
            new_transport = data.get("new_transport")
            new_price = data.get("new_price")

            if not route_id or not new_transport or not new_price:
                return {"message": "Missing required fields in request"}
            await self.route_service.change_transport(route_id, new_transport, new_price)
            
            return {"message": "Transport updated successfully"}
        except Exception as e:
            return {"message": "Error updating transport", "error": str(e)}
    
    async def get_route_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route_id = data.get("id")
            if route_id is None:
                return {"message": "Missing 'id' in request"}
            route = await self.route_service.get_by_id(route_id)
            if route and route.d_route is not None and route.travels is not None:
                return {
                    "route": {
                        "id": route.route_id,
                        "d_route_id": route.d_route.d_route_id,
                        "travel_id": route.travels.travel_id,
                        "start_time": route.start_time,
                        "end_time": route.end_time,
                        "route_id": route.route_id 
                    }
                }
            return {"message": "Route not found"}
        except Exception as e:
            return {"message": "Error fetching details", "error": str(e)}

    async def delete_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route_id = data.get("id")
            if route_id is None:
                return {"message": "Missing 'id' in request"}
            await self.route_service.delete(route_id)
            return {"message": "Route deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting route", "error": str(e)}
    
    async def get_all_route(self) -> dict[str, Any]:
        try:
            route_list = await self.route_service.get_all_routes()
            return {
                "routes": [
                    {
                        "id": r.route_id,
                        "d_route_id": r.d_route.d_route_id,
                        "travel_id": r.travels.travel_id,
                        "start_time": r.start_time,
                        "end_time": r.end_time,
                        "route_id": r.route_id 
                    }
                    for r in route_list if r is not None and r.d_route is not None and r.travels is not None
                ]
            }
        except Exception as e:
            return {"message": "Error fetching routes", "error": str(e)}
