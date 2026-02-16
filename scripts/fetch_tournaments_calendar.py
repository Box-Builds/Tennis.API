import json
from datetime import datetime
from pathlib import Path

import requests


URL = "https://www.atptour.com/en/-/tournaments/calendar/tour"
HEADERS = {"User-Agent": "TennisAPI/1.0 (Unofficial ATP wrapper)"}


def main() -> None:
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    tournaments_json = resp.json()

    # Save into /data with a datestamp so you can track updates
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.utcnow().strftime("%Y%m%d")
    out_path = data_dir / f"tournaments_calendar_raw_{stamp}.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(tournaments_json, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
