import json
from pathlib import Path
from typing import List, Dict, Any


def build_tournament_registry(raw_path: Path) -> List[Dict[str, Any]]:
    with raw_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    parsed: List[Dict[str, Any]] = []

    for date_block in data.get("TournamentDates", []):
        for tourney in date_block.get("Tournaments", []):
            parsed.append(
                {
                    "Id": str(tourney.get("Id")),
                    "Name": tourney.get("Name"),
                    "SglDrawSize": tourney.get("SglDrawSize"),
                    "DblDrawSize": tourney.get("DblDrawSize"),
                    "Type": tourney.get("Type"),
                }
            )

    return parsed


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"

    raw_files = sorted(data_dir.glob("tournaments_calendar_raw_*.json"))
    if not raw_files:
        print("No raw calendar files found.")
        return

    latest_raw = raw_files[-1]
    print(f"Using raw file: {latest_raw.name}")

    new_entries = build_tournament_registry(latest_raw)

    registry_path = data_dir / "tournament_registry.json"

    # Load existing registry if it exists
    if registry_path.exists():
        with registry_path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing_by_id = {t["Id"]: t for t in existing}

    added = 0

    for entry in new_entries:
        tid = entry["Id"]
        if tid not in existing_by_id:
            existing_by_id[tid] = entry
            added += 1

    merged = list(existing_by_id.values())

    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

    print(f"Registry updated. {added} new tournaments added.")
    print(f"Total tournaments in registry: {len(merged)}")


if __name__ == "__main__":
    main()
