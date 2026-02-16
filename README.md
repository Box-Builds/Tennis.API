# ATP Tennis API

Unofficial ATP Tour API wrapper built with FastAPI.

Version: 1.0.0

This project provides structured, programmatic access to ATP tournament, match, and head-to-head data using the ATP Tour website endpoints.

---

## 🚀 Features

- Tournament calendar fetching
- Tournament registry builder
- Match data endpoints
- Head-to-Head (H2H) endpoint
- Flattened + unflattened H2H formats
- Clean modular FastAPI structure
- Script utilities for maintaining tournament registry

---

## 🛠 Installation

### Clone the repository:

```bash
git clone https://github.com/Box-Builds/Tennis.API.git
cd Tennis.API
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the API locally:
```bash
uvicorn main:app --reload
```

### API will be available at:

http://127.0.0.1:8000/docs

## 📡 Endpoints

Base route:
```bash
/atp
```
### Tournaments
```bash
GET /atp/tournaments
```
### Matches
```bash
GET /atp/matches/{tournament_id}
```
### Head-to-Head
```bash
GET /atp/h2h/{player1_id}/{player2_id}
```

Optional flatten mode:
```bash
GET /atp/h2h/DH58/AG37?flatten=true
```
## 🧠 H2H Schema Note

The ATP Tour website uses two different H2H schemas:
```bash
/tour/Head2HeadSearch/GetHead2HeadData

/www/h2h/{id1}/{id2}
```
This API uses the GetHead2HeadData schema for consistency and stability.

Flattened mode provides simplified match metadata while preserving upstream team structures.

## 📂 Project Structure
api/            → FastAPI route definitions
utils/          → ATP data utilities and parsers
scripts/        → Registry and calendar maintenance tools
data/           → Tournament registry + cached calendar data
main.py         → FastAPI application entry point

### 🔄 Tournament Registry System

The registry is maintained via:

scripts/fetch_tournaments_calendar.py
scripts/build_tournament_registry.py


### Workflow:

Fetch latest ATP calendar JSON

Build/merge tournament registry

Registry acts as key lookup for historical matches

## ⚠ Disclaimer

This is an unofficial API wrapper and is not affiliated with the ATP Tour.

## 🏗 Built By Box-Builds

## 🔮 Roadmap / Future Improvements

Planned improvements for upcoming versions:

Add WTA Tour support

Improve flattened match normalization

Add optional client wrapper class (from tennis_api import TennisAPI)

Add response models (Pydantic schemas) for stricter typing

Add basic caching layer for frequently requested endpoints

Improve match-level stat extraction consistency

Docker container configuration

Add automated tests
