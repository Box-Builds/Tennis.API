# api/h2h.py
from fastapi import APIRouter, HTTPException, Query
from utils.atp_h2h import fetch_head_to_head, flatten_h2h_matches
from typing import Dict, Any

router = APIRouter()


@router.get(
    "/{player1_id}/{player2_id}",
    summary="Get head-to-head matches between two ATP players",
)
async def get_head_to_head(
    player1_id: str,
    player2_id: str,
    flatten: bool = Query(False, description="Return simplified match metadata"),
):
    """
    Returns head-to-head matches between two ATP players.

    - flatten=False → returns raw upstream H2H JSON (exact ATP response)
    - flatten=True  → returns simplified flattened match metadata
    """
    try:
        raw_json: Dict[str, Any] = await fetch_head_to_head(player1_id, player2_id)

        if not flatten:
            return raw_json

        # Upstream schema uses lowercase playerLeft/playerRight
        player_left = raw_json.get("playerLeft")
        player_right = raw_json.get("playerRight")

        flattened = flatten_h2h_matches(raw_json)

        return {
            "playerLeft": player_left,
            "playerRight": player_right,
            "matches": flattened,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch head-to-head data")
