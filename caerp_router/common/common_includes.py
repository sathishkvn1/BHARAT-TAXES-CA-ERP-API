

from fastapi import APIRouter
from caerp_auth import authentication
from caerp_router.common import  common,otp_process,user
from caerp_functions import captcha

common_router = APIRouter()

# Include routers for the common module
common_router.include_router(authentication.router)
common_router.include_router(common.router)
common_router.include_router(otp_process.router)
common_router.include_router(user.router)
common_router.include_router(captcha.router)
