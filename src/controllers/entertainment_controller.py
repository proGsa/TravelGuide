from __future__ import annotations

from typing import Any

from fastapi import Request

from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


class EntertainmentController:
    def __init__(self, entertainment_service: EntertainmentService) -> None:
        self.entertainment_service = entertainment_service

    async def create_new_entertainment(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment = Entertainment(
                entertainment_id=1, 
                duration=data.get('duration'),
                address=data.get('address'),
                event_name=data.get('event_name'),
                event_time=data.get('event_time')
            )
            await self.entertainment_service.add(entertainment)
            return {"message": "Entertainment created successfully"}
        except Exception as e:
            return {"message": "Error creating entertainment", "error": str(e)}

    async def update_entertainment(self, entertainment_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment = Entertainment(
                entertainment_id=entertainment_id,
                duration=data.get('duration'),
                address=data.get('address'),
                event_name=data.get('event_name'),
                event_time=data.get('event_time')
            )
            await self.entertainment_service.update(entertainment)
            return {"message": "Entertainment updated successfully"}
        except Exception as e:
            return {"message": "Error updating entertainment", "error": str(e)}
            
    async def get_entertainment_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment_id = data.get("id")
            if entertainment_id is None:
                return {"message": "Missing 'id' in request"}
            entertainment = await self.entertainment_service.get_by_id(entertainment_id)
            if entertainment:
                return {
                    "entertainment": {
                        "id": entertainment.entertainment_id,
                        "duration": entertainment.duration,
                        "address": entertainment.address,
                        "event_name": entertainment.event_name,
                        "event_time": entertainment.event_time.isoformat()
                        }
                }
            return {"message": "Entertainment not found"}
        except Exception as e:
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_entertainment(self) -> dict[str, Any]:
        try:
            entertainment_list = await self.entertainment_service.get_list()
            return {
                "entertainments": [
                    {
                        "id": e.entertainment_id,
                        "duration": e.duration,
                        "address": e.address,
                        "event_name": e.event_name,
                        "event_time": e.event_time.isoformat()
                    }
                    for e in entertainment_list
                ]
            }
        except Exception as e:
            return {"message": "Error fetching entertainments", "error": str(e)}

    async def delete_entertainment(self, entertainment_id: int) -> dict[str, Any]:
        try:
            await self.entertainment_service.delete(entertainment_id)
            return {"message": "Entertainment deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting entertainment", "error": str(e)}