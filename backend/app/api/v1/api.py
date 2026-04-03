"""
API Router Aggregation
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, lobsters, search, tags

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(lobsters.router, prefix="/lobsters", tags=["Lobsters"])
api_router.include_router(search.router, prefix="/search", tags=["搜索"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签"])
