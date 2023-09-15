from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_offlineshop")

offlineshop_static_files = [
    {
        "path": "/offlineshop/static",
        "name": "offlineshop_static",
    }
]

offlineshop_ext: APIRouter = APIRouter(prefix="/offlineshop", tags=["Offlineshop"])


def offlineshop_renderer():
    return template_renderer(["offlineshop/templates"])


from .lnurl import *  # noqa: F401,F403
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403
