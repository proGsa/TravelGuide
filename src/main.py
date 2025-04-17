from __future__ import annotations

from fastapi import FastAPI

from routers.accommodation import accommodation_router
from routers.entertainment import entertainment_router
from routers.travel import travel_router
from routers.user import user_router


app = FastAPI()
app.include_router(user_router)
app.include_router(accommodation_router)
app.include_router(entertainment_router)
app.include_router(travel_router)