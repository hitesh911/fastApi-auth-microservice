from fastapi import APIRouter
from . import access_manager
router = APIRouter(prefix="/admin")

router.include_router(access_manager.router)
    