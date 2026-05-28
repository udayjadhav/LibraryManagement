from fastapi import APIRouter

from app.api import books, borrowings, health, members

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(books.router)
api_router.include_router(members.router)
api_router.include_router(borrowings.router)
