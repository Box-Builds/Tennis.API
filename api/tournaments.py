# api/tournaments.py
from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REGISTRY_FILE = DATA_DIR / "tournament_registry.json"


@router.get("/registry", summary="Get tournament registry (cumulative IDs)")
async def get_registry():
    if not REGISTRY_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Missing data file: {REGISTRY_FILE.name}",
        )

    try:
        with REGISTRY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON in: {REGISTRY_FILE.name}",
        )
