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
            entertainment = Entertainment(**data)
            await self.entertainment_service.add(entertainment)
            return {"message": "Entertainment created successfully"}
        except Exception as e:
            return {"message": "Error creating entertainment", "error": str(e)}

    async def update_entertainment(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment = Entertainment(**data)
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
                        "address": entertainment.location,
                        "event_name": entertainment.a_type,
                        "event_time": entertainment.datetime.isoformat()
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
                        "address": e.location,
                        "event_name": e.a_type,
                        "event_time": e.datetime.isoformat()
                    }
                    for e in entertainment_list
                ]
            }
        except Exception as e:
            return {"message": "Error fetching entertainments", "error": str(e)}

    async def delete_entertainment(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment_id = data.get("id")
            if entertainment_id is None:
                return {"message": "Missing 'id' in request"}
            await self.entertainment_service.delete(entertainment_id)
            return {"message": "Entertainment deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting entertainment", "error": str(e)}