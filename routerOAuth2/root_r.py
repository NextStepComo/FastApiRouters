from fastapi import APIRouter
from routerOAuth2.auth import router as auth_r
from routerOAuth2.dataAcquisition import router as acqu_r

router = APIRouter()

router.include_router(auth_r.router)
router.include_router(acqu_r.router)
