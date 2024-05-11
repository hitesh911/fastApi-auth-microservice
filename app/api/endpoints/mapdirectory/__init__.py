from fastapi import APIRouter
from . import evplaces

router = APIRouter(prefix="/mapdirectory")

router.include_router(evplaces.router)

    