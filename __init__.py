from fastapi import APIRouter

from .crud import db
from .views import offlineshop_generic_router
from .views_api import offlineshop_api_router
from .views_lnurl import offlineshop_lnurl_router

offlineshop_static_files = [
    {
        "path": "/offlineshop/static",
        "name": "offlineshop_static",
    }
]

offlineshop_ext: APIRouter = APIRouter(prefix="/offlineshop", tags=["Offlineshop"])
offlineshop_ext.include_router(offlineshop_generic_router)
offlineshop_ext.include_router(offlineshop_api_router)
offlineshop_ext.include_router(offlineshop_lnurl_router)

__all__ = ["offlineshop_ext", "offlineshop_static_files", "db"]
