# ATP Tennis API

Unofficial ATP Tour API wrapper built with **FastAPI**.

Version: **1.0.0**

This project provides structured, programmatic access to ATP tournament, match, and head-to-head data by wrapping the ATP Tour website endpoints and exposing them through a clean REST API.

---

# Overview

The official ATP Tour website exposes rich tennis data but does not provide a public developer API.  
This project reverse-engineers those endpoints and converts them into a structured, developer-friendly interface.

The API allows developers and analysts to programmatically retrieve:

- tournament information
- match data
- head-to-head statistics
- structured historical tennis data

The goal is to make ATP data **accessible for analysis, tooling, and automation**.

---

# Features

- Tournament calendar fetching
- Tournament registry builder
- Match data endpoints
- Head-to-Head (H2H) endpoint
- Flattened and unflattened H2H formats
- Modular **FastAPI** architecture
- Script utilities for maintaining tournament registry data

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Box-Builds/Tennis.API.git
cd Tennis.API
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn main:app --reload
```

Interactive API documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

Base route:

```text
/atp
```

## Tournaments

```http
GET /atp/tournaments
```

Returns the registered ATP tournament dataset.

---

## Matches

```http
GET /atp/matches/{tournament_id}
```

Returns match data for a specific ATP tournament.

---

## Head-to-Head

```http
GET /atp/h2h/{player1_id}/{player2_id}
```

Returns head-to-head statistics for two players.

Optional flattened output:

```http
GET /atp/h2h/DH58/AG37?flatten=true
```

---

## Example Request

```http
GET /atp/h2h/DH58/AG37?flatten=true
```

## Example Response

```json
{
  "playerLeft": {
    "winCount": 2,
    "ranking": 6,
    "Age": 27,
    "BirthPlace": "Australia",
    "HeightCm": 183,
    "WeightKg": 69,
    "PlayHand": "R",
    "ProYear": 2015,
    "CareerTitles": 11,
    "CareerPrizeMoney": 24237259,
    "winPercentage": 40,
    "id": "DH58",
    "firstName": "Alex",
    "lastName": "de Minaur",
    "PlayerCountryCode": "AUS"
  },
  "playerRight": {
    "winCount": 3,
    "ranking": 9,
    "Age": 25,
    "BirthPlace": "Canada",
    "HeightCm": 193,
    "WeightKg": 88,
    "PlayHand": "R",
    "ProYear": 2017,
    "CareerTitles": 9,
    "CareerPrizeMoney": 21553400,
    "winPercentage": 60,
    "id": "AG37",
    "firstName": "Felix",
    "lastName": "Auger-Aliassime",
    "PlayerCountryCode": "CAN"
  },
  "matches": [
    {
      "tournament": "Rotterdam",
      "year": 2026,
      "round": "F",
      "winner": "DH58",
      "surface": "Hard",
      "indoor_outdoor": "Indoor",
      "match_id": "MS001",
      "result": null,
      "sets": null,
      "player_team": {
        "PlayerId": "DH58",
        "PlayerFirstName": "A.",
        "PlayerLastName": "de Minaur",
        "PlayerCountryCode": "AUS"
      },
      "opponent_team": {
        "PlayerId": "AG37",
        "PlayerFirstName": "F.",
        "PlayerLastName": "Auger-Aliassime",
        "PlayerCountryCode": "CAN"
      },
      "upstream_sets": [
        {
          "set_number": 1,
          "player_games": 6,
          "player_tiebreak": null,
          "won_set": false
        },
        {
          "set_number": 2,
          "player_games": 6,
          "player_tiebreak": null,
          "won_set": false
        }
      ],
      "match_stats_url": null,
      "reason": null
    }
  ]
}
```

---

# H2H Schema Note

The ATP website exposes **two different H2H data schemas**:

```text
/tour/Head2HeadSearch/GetHead2HeadData
/www/h2h/{id1}/{id2}
```

This API standardizes around the **GetHead2HeadData** schema to ensure consistent structure and easier downstream processing.

The optional `flatten` mode provides simplified match metadata while preserving the upstream team data structure.

---

# Project Structure

```text
api/        → FastAPI route definitions
utils/      → ATP data utilities and parsing logic
scripts/    → Registry and calendar maintenance tools
data/       → Tournament registry and cached calendar data
main.py     → FastAPI application entry point
```

---

# Tournament Registry System

ATP tournaments change slightly each season, so this project maintains a registry system to map tournament identifiers across years.

The registry is maintained with the following scripts:

```text
scripts/fetch_tournaments_calendar.py
scripts/build_tournament_registry.py
```

### Workflow

1. Fetch the latest ATP calendar JSON
2. Build or merge the tournament registry
3. Use the registry as a lookup key for historical match queries

This allows stable tournament lookups across multiple seasons.

---

# Roadmap / Future Improvements

Planned improvements for upcoming versions:

- Add **WTA Tour support**
- Improve flattened match normalization
- Add optional Python client wrapper  
  (`from tennis_api import TennisAPI`)
- Introduce response models using **Pydantic schemas**
- Add caching for frequently requested endpoints
- Improve match-level stat extraction
- Provide Docker container configuration
- Add automated tests

---

# Disclaimer

This is an **unofficial API wrapper** and is not affiliated with the ATP Tour.

This project simply provides a structured interface for publicly accessible ATP website data.

---

# Author

Built by **Box-Builds**
