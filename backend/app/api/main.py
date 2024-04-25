"""
    This file is used to include all the routers in the APIRouter.
"""
from fastapi import APIRouter

from app.api.routes import financial_instruments,users,oauth,trades,home_page

api_router = APIRouter()
api_router.include_router(financial_instruments.router, prefix="/financial_instruments",tags=["financial instruments"])
api_router.include_router(users.router, prefix="/users",tags=["users"])
api_router.include_router(oauth.router, prefix="/oauth",tags=["oauth"])
api_router.include_router(trades.router, prefix="/trades",tags=["trades"])
api_router.include_router(home_page.router, tags=["home page"])
