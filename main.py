"""
ATP Tennis API
Version: 1.0.0
"""
from fastapi import FastAPI
from api.api import router as atp_router

app = FastAPI(title="ATP Tennis API")
app.include_router(atp_router, prefix="/atp")
