# City Break Planner – Backend (DB setup)

## 1. Start PostgreSQL + PostGIS

From the **project root** (`travel/`):

```bash
docker compose up -d
```

Verify PostGIS:

```bash
docker compose exec db psql -U citybreak -d citybreak -c "SELECT PostGIS_Version();"
```

## 2. Python environment and dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional: set `DATABASE_URL` (default is `postgresql+psycopg2://citybreak:citybreak@localhost:5432/citybreak`):

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/citybreak"
```

## 3. Create tables

Run the init script (ensures PostGIS extension exists and creates all tables):

```bash
# From backend/
python -m scripts.init_db
```

Or from project root:

```bash
cd backend && python -m scripts.init_db
```

Tables created: `locations`, `pois`, `itineraries`, `daily_routes`, `route_stops`.

## 4. Run the API

```bash
# From backend/ with venv active
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **POST** `/api/v1/itineraries/generate` — body: `{"city_name": "Cluj-Napoca", "days": 3, "pace": "moderate"}`.
- **GET** `/api/v1/itineraries/{itinerary_id}` — retrieve itinerary.
- **GET** `/api/v1/routes/{daily_route_id}/geometry` — GeoJSON LineString for the map (optional: set `MAPBOX_ACCESS_TOKEN` for real walking routes).
