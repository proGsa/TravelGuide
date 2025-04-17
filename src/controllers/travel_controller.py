from __future__ import annotations

from typing import Any

from fastapi import Request

from models.travel import Travel
from services.travel_service import TravelService


class TravelController:
    def __init__(self, travel_service: TravelService) -> None:
        self.travel_service = travel_service

    async def create_new_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel = Travel(**data)
            await self.travel_service.add(travel)
            return {"message": "Travel created successfully"}
        except Exception as e:
            return {"message": "Error creating travel", "error": str(e)}
        
    async def get_travel_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_id = data.get("id")
            if travel_id is None:
                return {"message": "Missing 'id' in request"}
            travel = await self.travel_service.get_by_id(travel_id)
            entertainment_list = await self.travel_service.get_entertainments_by_travel(travel_id)
            accommodation_list = await self.travel_service.get_accommodations_by_travel(travel_id)
            if travel and travel.users:
                return {
                    "travel": {
                        "id": travel.travel_id,
                        "status": travel.status,
                        "user_id": travel.users.user_id,
                        "entertainments": [
                            {
                                "id": e.entertainment_id,
                                "duration": e.duration,
                                "address": e.address,
                                "event_name": e.event_name,
                                "event_time": e.event_time.isoformat()
                            }
                            for e in entertainment_list
                        ],
                         "accommodations": [
                            {
                                "id": a.accommodation_id,
                                "price": a.price,
                                "address": a.address,
                                "name": a.name,
                                "e_type": a.type,
                                "rating": a.rating,
                                "check_in": a.check_in.isoformat(),
                                "check_out": a.check_out.isoformat()
                            }
                            for a in accommodation_list
                        ]
                    }
                }
            return {"message": "Entertainment not found"}
        except Exception as e:
            return {"message": "Error fetching details", "error": str(e)}

    async def complete_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_id = data.get("id")
            if travel_id is None:
                return {"message": "Missing 'id' in request"}
            await self.travel_service.complete(travel_id)
            return {"message": "Travel completed successfully"}
        except Exception as e:
            return {"message": "Error complete travel", "error": str(e)}

    async def check_archive_travels(self) -> dict[str, Any]:
        try:
            archived_travels = await self.travel_service.check_archive()
            return {"archived_travels": archived_travels}
        except Exception as e:
            return {"message": "Error checking archive travels", "error": str(e)}

    async def update_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel = Travel(**data)
            await self.travel_service.update(travel)
            return {"message": "Travel updated successfully"}
        except Exception as e:
            return {"message": "Error updating travel", "error": str(e)}
    
    async def delete_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_id = data.get("id")
            if travel_id is None:
                return {"message": "Missing 'id' in request"}
            await self.travel_service.delete(travel_id)
            return {"message": "Travel deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting travel", "error": str(e)}

    async def search_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_dict = data.get("search")
            
            if not travel_dict:
                return {"message": "Missing search parameters"}
            
            search_results = await self.travel_service.search(travel_dict)
            return {"search_results": search_results}
        
        except Exception as e:
            return {"message": "Error searching for travel", "error": str(e)}

    async def get_all_travels(self) -> dict[str, Any]:
        try:
            travel_list = await self.travel_service.get_all_travels()
            
            travels = []
            for t in travel_list:
                entertainment_list = await self.travel_service.get_entertainments_by_travel(t.travel_id)
                accommodation_list = await self.travel_service.get_accommodations_by_travel(t.travel_id)
                if t.users:
                    travels.append({
                        "id": t.travel_id,
                        "status": t.status,
                        "user_id": t.users.user_id,
                        "entertainments": [
                            {
                                "id": e.entertainment_id,
                                "duration": e.duration,
                                "address": e.address,
                                "event_name": e.event_name,
                                "event_time": e.event_time.isoformat()
                            }
                            for e in entertainment_list
                        ],
                        "accommodations": [
                            {
                                "id": a.accommodation_id,
                                "price": a.price,
                                "address": a.address,
                                "name": a.name,
                                "e_type": a.type,
                                "rating": a.rating,
                                "check_in": a.check_in.isoformat(),
                                "check_out": a.check_out.isoformat()
                            }
                            for a in accommodation_list
                        ]
                    })

            return {"travels": travels}
        
        except Exception as e:
            return {"message": "Error fetching travels", "error": str(e)}
