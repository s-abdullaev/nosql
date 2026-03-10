# NoSQL Demo

FastAPI application with MongoDB, Redis, and PostGIS (PostgreSQL). MongoDB is seeded from the university schema (database/sql/DDL.sql, DML.sql). PostGIS provides spatial data (restaurants, regions in Paris) managed via Alembic migrations.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (or pip)
- Docker & Docker Compose

## How to Run

1. **Start all services**

   ```bash
   docker compose up -d
   ```

   | Service  | Port  | Credentials             |
   |----------|-------|-------------------------|
   | MongoDB  | 27017 | admin / password        |
   | Redis    | 6379  | (no auth)               |
   | PostGIS  | 5432  | postgres / postgres     |

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Seed MongoDB**

   ```bash
   uv run python -m database.mongodb.seed
   ```

   Creates the `university` database, collections, indexes, and sample data. **Warning:** seed drops the database first (destructive, re-runnable).

4. **Run PostGIS migrations**

   ```bash
   uv run alembic upgrade head
   ```

   Enables the PostGIS extension, creates `restaurant` and `region` tables, and seeds sample geodata (Paris restaurants and neighborhoods).

5. **Start the API**

   ```bash
   uv run python main.py
   ```

   Or with auto-reload for development:

   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - API: http://localhost:8000  
   - Docs: http://localhost:8000/docs

## Environment

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

| Variable        | Default                                    | Description              |
|-----------------|--------------------------------------------|--------------------------|
| `MONGO_URI`     | `mongodb://admin:password@localhost:27017`  | MongoDB connection string |
| `MONGO_DB_NAME` | `university`                               | Database name            |
| `REDIS_URL`     | `redis://localhost:6379/0`                 | Redis connection URL     |
| `POSTGRES_URL`  | `postgresql://postgres:postgres@localhost:5432/geodemo` | PostGIS connection URL |

The FastAPI app uses these. The seed script uses `database/mongodb/seed.py` and its own hardcoded connection string.

## How to Make Changes

| What to change | Where |
|----------------|-------|
| **API routes** | `app/routes/mongodb.py`, `app/routes/redis.py`, `app/routes/postgis.py` |
| **Request/response models** | `app/schema.py` |
| **Database connections** | `app/database.py` (Mongo + PostGIS), `config.py` |
| **MongoDB schema & seed data** | `database/mongodb/seed.py` |
| **PostGIS models** | `app/models.py` (SQLAlchemy + GeoAlchemy2) |
| **PostGIS migrations** | `alembic/versions/` — create new with `uv run alembic revision -m "description"` |
| **SQL schema (reference)** | `database/sql/DDL.sql`, `database/sql/DML.sql` |
| **Add new routers** | `app/main.py` — import and `app.include_router(...)` |

**Development workflow:** Run the API with `--reload` so changes apply automatically. Re-run the seed script after changing `database/mongodb/seed.py`. For PostGIS schema changes, create a new Alembic migration and run `uv run alembic upgrade head`.

## Working with MongoDB

### Connect via mongosh

```bash
mongosh "mongodb://admin:password@localhost:27017"
```

### Collections (schema)

| Collection           | Description                          |
|----------------------|--------------------------------------|
| `course`             | Courses and credits                  |
| `student`            | Students and total credits           |
| `takes`              | Student enrollments and grades       |
| `student_enrollments`| Students with embedded enrollments   |

### Example queries (mongosh)

```javascript
use university

// All courses
db.course.find()

// All Comp. Sci. courses
db.course.find({ dept_name: "Comp. Sci." })

// Students with more than 100 credits
db.student.find({ tot_cred: { $gt: 100 } })

// Enrollments in Fall 2017
db.takes.find({ semester: "Fall", year: 2017 })
```

### Using PyMongo in Python

```python
from app.database import get_db

db = get_db()
courses = list(db.course.find({"dept_name": "Comp. Sci."}, {"_id": 0}))
students = list(db.student.find({}, {"_id": 0}))
enrollments = list(db.student_enrollments.find({}, {"_id": 0}))
```

### API Endpoints

| Endpoint | Description |
|----------|--------------|
| `GET /` | Hello message |
| `GET /health` | Health check |
| `GET /mongodb/students` | List all students |
| `GET /mongodb/students/credits` | List students with aggregated credits from enrollments |
| `GET /mongodb/students/credits/by-dept?dept_name=` | Same, filtered by department |
| `POST /mongodb/students` | Create a student |
| `PUT /mongodb/students/{student_id}` | Update a student |
| `DELETE /mongodb/students/{student_id}` | Delete a student |
| `GET /mongodb/student_enrollments` | List all students with their enrolled courses |
| `POST /mongodb/students/{student_id}/enrollments` | Add an enrollment |
| `DELETE /mongodb/students/{student_id}/enrollments` | Remove an enrollment |

## Working with Redis

Redis (via Redis Stack) provides key-value storage for strings, lists, hashes, and JSON objects.

### Connect via redis-cli

```bash
redis-cli -h localhost -p 6379
```

### Redis API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /redis/string/{key}` | Set a string value (body: JSON string, e.g. `"world"`) |
| `GET /redis/string/{key}` | Get a string value |
| `POST /redis/list/{key}/push` | Push a value onto the list (body: JSON value) |
| `POST /redis/list/{key}/pop` | Pop a value from the end of the list |
| `GET /redis/list/{key}` | Get all values in the list |
| `POST /redis/hash/{key}/{field}` | Set a field in a hash (body: JSON string value) |
| `GET /redis/hash/{key}/{field}` | Get a field from a hash |
| `POST /redis/json/{key}` | Set a JSON object (body: JSON object) |
| `GET /redis/json/{key}` | Get JSON at root |
| `GET /redis/json/{key}/{path}` | Get JSON at path (e.g. `.name`, `.address.city`) |

## Working with PostGIS

PostgreSQL with the PostGIS extension stores geographic data (points, polygons). Tables are managed via SQLAlchemy + GeoAlchemy2 models; schema and seed data are applied through Alembic migrations.

### Connect via psql

```bash
docker exec -it postgis psql -U postgres -d geodemo
```

### Tables

| Table        | Geometry Column | Type    | Description                         |
|--------------|-----------------|---------|-------------------------------------|
| `restaurant` | `location`      | POINT   | Paris restaurants with coordinates  |
| `region`     | `boundary`      | POLYGON | Paris neighborhoods as polygons     |

### Example queries (psql)

```sql
-- All restaurants with readable coordinates
SELECT name, cuisine, ST_AsText(location) FROM restaurant;

-- All regions with area in square meters
SELECT name, ST_Area(Geography(boundary)) AS area_m2 FROM region;

-- Restaurants within 500 m of Café de Flore
SELECT r.name, ST_Distance(Geography(r.location), Geography(f.location)) AS dist_m
FROM restaurant r, restaurant f
WHERE f.name = 'Café de Flore'
  AND ST_DWithin(Geography(r.location), Geography(f.location), 500)
  AND r.id != f.id
ORDER BY dist_m;

-- Restaurants inside Saint-Germain-des-Prés
SELECT r.name
FROM restaurant r
JOIN region reg ON ST_Contains(reg.boundary, r.location)
WHERE reg.name = 'Saint-Germain-des-Prés';

-- Intersection area between two regions
SELECT ST_Area(Geography(ST_Intersection(a.boundary, b.boundary))) AS area_m2
FROM region a, region b
WHERE a.name = 'Saint-Germain-des-Prés' AND b.name = 'Rive Gauche Centre';
```

### PostGIS API Endpoints

**CRUD — Restaurants**

| Endpoint | Description |
|----------|-------------|
| `GET /postgis/restaurants` | List all restaurants |
| `POST /postgis/restaurants` | Create a restaurant (body: name, cuisine, address, latitude, longitude) |
| `GET /postgis/restaurants/{id}` | Get a restaurant |
| `PUT /postgis/restaurants/{id}` | Update a restaurant |
| `DELETE /postgis/restaurants/{id}` | Delete a restaurant |

**CRUD — Regions**

| Endpoint | Description |
|----------|-------------|
| `GET /postgis/regions` | List all regions |
| `POST /postgis/regions` | Create a region (body: name, description, coordinates as `[[lon, lat], ...]`) |
| `GET /postgis/regions/{id}` | Get a region |
| `PUT /postgis/regions/{id}` | Update a region |
| `DELETE /postgis/regions/{id}` | Delete a region |

**Spatial Queries**

| Endpoint | Description |
|----------|-------------|
| `GET /postgis/restaurants/distance?latitude=&longitude=` | Distance (meters) from a point to every restaurant, sorted nearest-first |
| `GET /postgis/restaurants/nearby?latitude=&longitude=&max_distance=` | Restaurants within a radius, sorted by distance |
| `GET /postgis/regions/{id}/restaurants` | Restaurants contained within a region (ST_Contains) |
| `GET /postgis/regions/{id}/area` | Area of a region in sq meters and sq km |
| `GET /postgis/regions/intersection?region1_id=&region2_id=` | Whether two regions intersect, with intersection geometry and area |

### Alembic Commands

```bash
uv run alembic upgrade head      # apply all migrations
uv run alembic downgrade -1      # rollback one migration
uv run alembic revision -m "msg" # create a new migration
uv run alembic current           # show current revision
```

---

Use the interactive API docs at http://localhost:8000/docs to try endpoints.
