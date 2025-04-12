from __future__ import annotations

from typing import Any

from fastapi import Request

from models.accommodation import Accommodation
from services.accommodation_service import AccommodationService


class AccommodationController:
    def __init__(self, accommodation_service: AccommodationService) -> None:
        self.accommodation_service = accommodation_service

    async def create_new_accommodation(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            accommodation = Accommodation(**data)
            await self.accommodation_service.add(accommodation)
            return {"message": "Entertainment created successfully"}
        except Exception as e:
            return {"message": "Error creating accommodation", "error": str(e)}
    
    async def update_accommodation(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            accommodation = Accommodation(**data)
            await self.accommodation_service.update(accommodation)
            return {"message": "Entertainment updated successfully"}
        except Exception as e:
            return {"message": "Error updating accommodation", "error": str(e)}
    
    async def get_accommodation_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            accommodation_id = data.get("id")
            if accommodation_id is None:
                return {"message": "Missing 'id' in request"}
            accommodation = await self.accommodation_service.get_by_id(accommodation_id)
            if accommodation:
                return {
                    "accommodation": {
                        "id": accommodation.accommodation_id,
                        "price": accommodation.cost,
                        "address": accommodation.address,
                        "name": accommodation.name,
                        "e_type": accommodation.e_type,
                        "rating": accommodation.rating,
                        "check_in": accommodation.entry_datetime.isoformat(),
                        "check_out": accommodation.departure_datetime.isoformat()
                    }
                }
            return {"message": "Accommodation not found"}
        except Exception as e:
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_accommodation(self) -> dict[str, Any]:
        try:
            accommodation_list = await self.accommodation_service.get_list()
            return {
                    "accommodations": [
                        {
                            "id": a.accommodation_id,
                            "price": a.cost,
                            "address": a.address,
                            "name": a.name,
                            "e_type": a.e_type,
                            "rating": a.rating,
                            "check_in": a.entry_datetime.isoformat(),
                            "check_out": a.departure_datetime.isoformat()
                        }
                        for a in accommodation_list
                    ]
                }
        except Exception as e:
            return {"message": "Error fetching accommodations", "error": str(e)}

    async def delete_accommodation(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            accommodation_id = data.get("id")
            if accommodation_id is None:
                return {"message": "Missing 'id' in request"}
            await self.accommodation_service.delete(accommodation_id)
            return {"message": "Accommodation deleted successfully"}
        except Exception as e:
            return {"message": "Error deleting accommodation", "error": str(e)}