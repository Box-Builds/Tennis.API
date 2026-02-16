# api/matches.py
from fastapi import APIRouter, HTTPException, Query
import httpx
import json
from pathlib import Path
from utils.match_ids import generate_match_ids, generate_qualifier_ids
from typing import Dict, Optional, Any, List

router = APIRouter()

HEADERS = {"User-Agent": "TennisAPI/1.0 (Unofficial ATP wrapper)"}

BASE_HAWKEYE_URL = "https://www.atptour.com/-/Hawkeye/MatchStats/Complete"
MAX_QUALIFIERS = 20  # fallback until you infer actual qualy size per event

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOURNAMENT_REGISTRY_FILE = DATA_DIR / "tournament_registry.json"

_TOURNAMENTS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def load_tournament_registry() -> Dict[str, Dict[str, Any]]:
    """
    Loads tournament_registry.json and returns a dict keyed by tournament Id (as string).
    Cached after first load.
    """
    global _TOURNAMENTS_CACHE
    if _TOURNAMENTS_CACHE is not None:
        return _TOURNAMENTS_CACHE

    if not TOURNAMENT_REGISTRY_FILE.exists():
        raise HTTPException(status_code=500, detail=f"Missing data file: {TOURNAMENT_REGISTRY_FILE.name}")

    try:
        with TOURNAMENT_REGISTRY_FILE.open("r", encoding="utf-8") as f:
            items = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in: {TOURNAMENT_REGISTRY_FILE.name}")

    _TOURNAMENTS_CACHE = {str(t["Id"]): t for t in items if "Id" in t}
    return _TOURNAMENTS_CACHE


def resolve_tournament_id(
    tournament_id_or_name: str,
    tournaments: Dict[str, Dict[str, Any]],
) -> Optional[str]:
    """
    Accepts:
    - Exact Id (string of digits)
    - Exact tournament name (case-insensitive)

    If numeric but not in registry, return it anyway (graceful fallback).
    """
    key = str(tournament_id_or_name)

    # Exact ID match
    if key in tournaments:
        return key

    # Name match
    lowered = key.lower()
    for tid, t in tournaments.items():
        if str(t.get("Name", "")).lower() == lowered:
            return tid

    # Graceful fallback: numeric IDs are allowed even if not in registry
    if key.isdigit():
        return key

    return None


async def fetch_match(
    client: httpx.AsyncClient, year: int, tournament_id: str, match_id: str
) -> Optional[dict]:
    url = f"{BASE_HAWKEYE_URL}/{year}/{tournament_id}/{match_id}"
    resp = await client.get(url)
    if resp.status_code != 200:
        return None
    try:
        return resp.json()
    except Exception:
        return None


def _get(obj: Any, path: str, default=None):
    """Safe nested dict getter: _get(d, 'A.B.C')"""
    cur = obj
    for key in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def _has_match_id(payload: Any) -> bool:
    """True if payload contains a match id in either wrapped or legacy schema."""
    if not isinstance(payload, dict):
        return False
    if isinstance(payload.get("Match"), dict) and payload["Match"].get("MatchId"):
        return True
    if payload.get("MatchId"):
        return True
    return False


def flatten_match_data(payload: dict) -> dict:
    """
    Flattens either:
      - Wrapped: {"Tournament": {...}, "Match": {...}}
      - Legacy:  {"MatchId": "...", ...}

    Tailored to actual Hawkeye Complete payloads (like your Doha example).
    """
    if not isinstance(payload, dict):
        return {}

    tournament = payload.get("Tournament", {}) if isinstance(payload.get("Tournament"), dict) else {}
    match = payload.get("Match", {}) if isinstance(payload.get("Match"), dict) else payload  # legacy fallback

    match_id = match.get("MatchId") or payload.get("MatchId")

    # Core fields
    round_short = _get(match, "Round.ShortName") or match.get("RoundName") or match.get("Round")
    surface = tournament.get("Court") or match.get("Surface") or payload.get("Surface")
    status = match.get("Status") or match.get("MatchStatus") or payload.get("Status")
    duration = match.get("MatchTimeTotal") or match.get("MatchTime")

    winner_id = match.get("WinningPlayerId") or match.get("Winner") or payload.get("Winner")

    # Players (prefer full names from PlayerTeam / OpponentTeam)
    p1 = _get(match, "PlayerTeam.Player") or {}
    p2 = _get(match, "OpponentTeam.Player") or {}

    def player_obj(p: dict) -> Optional[dict]:
        if not isinstance(p, dict) or not p.get("PlayerId"):
            return None
        return {
            "player_id": p.get("PlayerId"),
            "first_name": p.get("PlayerFirstName"),
            "last_name": p.get("PlayerLastName"),
            "country": p.get("PlayerCountry"),
        }

    players: List[dict] = [x for x in [player_obj(p1), player_obj(p2)] if x]

    # Score by set (use PlayerTeam1/2 Sets arrays)
    p1_sets = _get(match, "PlayerTeam1.Sets", default=[])
    p2_sets = _get(match, "PlayerTeam2.Sets", default=[])

    score: List[dict] = []
    if isinstance(p1_sets, list) and isinstance(p2_sets, list) and (p1_sets or p2_sets):
        p1_by_set = {s.get("SetNumber"): s for s in p1_sets if isinstance(s, dict)}
        p2_by_set = {s.get("SetNumber"): s for s in p2_sets if isinstance(s, dict)}

        set_numbers = sorted({k for k in (set(p1_by_set.keys()) | set(p2_by_set.keys()))
                              if isinstance(k, int) and k >= 1})

        for n in set_numbers:
            s1 = p1_by_set.get(n, {})
            s2 = p2_by_set.get(n, {})
            tb1 = s1.get("TieBreakScore")
            tb2 = s2.get("TieBreakScore")

            score.append({
                "set": n,
                "p1": s1.get("SetScore"),
                "p2": s2.get("SetScore"),
                "tiebreak": None if (tb1 is None and tb2 is None) else {"p1": tb1, "p2": tb2},
            })

    return {
        "match_id": match_id,
        "event_id": tournament.get("EventId"),
        "event_year": tournament.get("EventYear"),
        "event_name": tournament.get("EventDisplayName"),
        "tournament_name": tournament.get("TournamentName"),
        "city": tournament.get("TournamentCity"),
        "surface": surface,
        "round": round_short,
        "status": status,
        "is_doubles": match.get("IsDoubles"),
        "winner_id": winner_id,
        "players": players or None,
        "score": score or None,
        "duration": duration,
    }


@router.get("/{year}/{tournament_id}", summary="Get all matches for a tournament")
async def get_tournament_matches(
    year: int,
    tournament_id: str,
    flatten: bool = Query(False, description="Return simplified match data"),
):
    tournaments = load_tournament_registry()

    tid_resolved = resolve_tournament_id(tournament_id, tournaments)
    if not tid_resolved:
        raise HTTPException(status_code=404, detail="Invalid tournament ID or name")

    tournament = tournaments.get(tid_resolved)  # may be None if numeric-but-not-in-registry
    draw_size = int(tournament.get("SglDrawSize", 32)) if tournament else 32

    main_match_ids = generate_match_ids(draw_size)
    qualy_match_ids = generate_qualifier_ids(MAX_QUALIFIERS)
    all_match_ids = main_match_ids + qualy_match_ids

    matches_data: Dict[str, Any] = {}

    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        for mid in all_match_ids:
            data = await fetch_match(client, year, tid_resolved, mid)
            if not data:
                continue

            # Filter out placeholder/junk responses (only keep if a MatchId exists)
            if not _has_match_id(data):
                continue

            matches_data[mid] = flatten_match_data(data) if flatten else data

    return {
        "tournament": tournament.get("Name") if tournament else "Unknown",
        "tournament_id": tid_resolved,
        "year": year,
        "matches": matches_data,
    }


@router.get("/{year}/{tournament_id}/{match_id}", summary="Get a single match")
async def get_single_match(
    year: int,
    tournament_id: str,
    match_id: str,
    flatten: bool = Query(False, description="Return simplified match data"),
):
    tournaments = load_tournament_registry()

    tid_resolved = resolve_tournament_id(tournament_id, tournaments)
    if not tid_resolved:
        raise HTTPException(status_code=404, detail="Invalid tournament ID or name")

    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        data = await fetch_match(client, year, tid_resolved, match_id)

    if not data:
        raise HTTPException(status_code=404, detail="Match not found")

    return {
        "tournament": tournaments.get(tid_resolved, {}).get("Name", "Unknown"),
        "tournament_id": tid_resolved,
        "year": year,
        "match_id": match_id,
        "match_data": flatten_match_data(data) if flatten else data,
    }
