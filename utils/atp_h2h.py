# utils/atp_h2h.py
import re
import httpx
from fastapi import HTTPException
from typing import Any, Dict, List, Optional
import re as _re

HEADERS = {"User-Agent": "TennisAPI/1.0 (Unofficial ATP wrapper)"}
BASE_H2H_URL = "https://www.atptour.com/en/-/tour/Head2HeadSearch/GetHead2HeadData"

_PLAYER_CODE_RE = re.compile(r"^[A-Za-z0-9]+$")

# e.g. "76(7)" -> games="76", tb="7"
_SET_TOKEN_RE = _re.compile(r"^(\d+)(?:\((\d+)\))?$")


async def fetch_head_to_head(player1_id: str, player2_id: str) -> Dict[str, Any]:
    if not _PLAYER_CODE_RE.match(player1_id) or not _PLAYER_CODE_RE.match(player2_id):
        raise HTTPException(
            status_code=400,
            detail="Player IDs must be alphanumeric ATP player codes (e.g., DH58)",
        )

    url = f"{BASE_H2H_URL}/{player1_id}/{player2_id}"

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10, follow_redirects=True) as client:
            resp = await client.get(url)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Upstream ATP request failed")

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Head-to-head not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Upstream ATP error (status {resp.status_code})")

    try:
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream ATP returned invalid JSON")


def parse_result_string(result: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Parses ATP ResultString if present (website schema).
    For upstream MatchResults schema, ResultString usually isn't present.
    """
    if not result or not isinstance(result, str):
        return None

    tokens = result.strip().split()
    out: List[Dict[str, Any]] = []
    set_num = 0

    for tok in tokens:
        upper = tok.upper()
        if upper in {"RET", "W/O", "WO", "DEF", "ABN", "BYE", "CANC"}:
            break

        m = _SET_TOKEN_RE.match(tok)
        if not m:
            continue

        digits = m.group(1)
        tb = m.group(2)
        if len(digits) < 2:
            continue

        p1_games = int(digits[0])
        p2_games = int(digits[1])

        set_num += 1
        out.append(
            {"set": set_num, "p1": p1_games, "p2": p2_games, "tiebreak": int(tb) if tb else None}
        )

    return out or None


def flatten_h2h_matches(raw_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flattens H2H matches into a single list.

    Supports BOTH:
      A) Upstream schema (your API fetch):
         tournament["TournamentName"], matches in tournament["MatchResults"]
         each match has PlayerTeam/OpponentTeam/Sets etc (NO ResultString)

      B) Website schema (/www/h2h/...):
         tournament["EventDisplayName"], matches in tournament["Matches"]
         each match has ResultString/MatchStatsUrl
    """
    matches: List[Dict[str, Any]] = []

    for section in ["Tournaments", "OtherTournaments"]:
        for tournament in raw_json.get(section, []) or []:
            if not isinstance(tournament, dict):
                continue

            # Tournament name differs by schema
            tournament_name = (
                tournament.get("TournamentName")
                or tournament.get("EventDisplayName")
                or tournament.get("EventName")
            )
            year = tournament.get("EventYear")
            surface = tournament.get("Surface")
            indoor_outdoor = tournament.get("InOutdoorDisplay")

            # Match list differs by schema
            match_list = tournament.get("MatchResults") or tournament.get("Matches") or []
            for match in match_list or []:
                if not isinstance(match, dict):
                    continue

                # Round shape differs slightly but both have Round.ShortName typically
                rnd = match.get("Round") or {}
                round_short = rnd.get("ShortName") if isinstance(rnd, dict) else None

                # Website schema includes ResultString; upstream doesn’t
                result = match.get("ResultString")
                sets_from_result = parse_result_string(result) if result else None

                # Upstream schema has sets nested under PlayerTeam/OpponentTeam as "Sets"
                upstream_sets = None
                pt = match.get("PlayerTeam") if isinstance(match.get("PlayerTeam"), dict) else None
                if pt and isinstance(pt.get("Sets"), list):
                    upstream_sets = [
                        {
                            "set_number": s.get("SetNumber"),
                            "player_games": s.get("SetScore"),
                            "player_tiebreak": s.get("TieBreakScore"),
                            "won_set": s.get("WonSet"),
                        }
                        for s in pt.get("Sets", [])
                    ]

                matches.append(
                    {
                        "tournament": tournament_name,
                        "year": year,
                        "round": round_short,
                        "winner": match.get("Winner"),
                        "surface": surface,
                        "indoor_outdoor": indoor_outdoor,
                        "match_id": match.get("MatchId"),
                        # Prefer website-style result parsing if present; otherwise include upstream set objects
                        "result": result,
                        "sets": sets_from_result,
                        "player_team": match.get("PlayerTeam"),
                        "opponent_team": match.get("OpponentTeam"),
                        "upstream_sets": upstream_sets,  # optional but useful since upstream lacks ResultString
                        "match_stats_url": match.get("MatchStatsUrl"),
                        "reason": match.get("Reason"),
                    }
                )

    return matches
