from app.api.base import router as base_router
from app.api.user import router as user_router
from app.api.category import router as category_router
from app.api.record import router as record_router
from app.api.card import router as card_router
from app.api.home import router as home_router

__all__ = ["base_router", "user_router", 
"category_router", "record_router", "card_router", "home_router"]
