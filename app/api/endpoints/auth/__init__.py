from fastapi import APIRouter
from . import otp ,user,admin, client , sub_client,policy
router = APIRouter(prefix="/auth")

router.include_router(otp.router)
router.include_router(user.router)
router.include_router(admin.router)
router.include_router(client.router)
router.include_router(sub_client.router)
router.include_router(policy.router)
    