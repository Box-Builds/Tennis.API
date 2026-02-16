from fastapi import APIRouter
from .tournaments import router as tournaments_router
from .matches import router as matches_router
from .h2h import router as h2h_router 

router = APIRouter()

# Include routers
router.include_router(tournaments_router, prefix="/tournaments", tags=["Tournaments"])
router.include_router(matches_router, prefix="/matches", tags=["Matches"])
router.include_router(h2h_router, prefix="/h2h", tags=["Players"]) 

