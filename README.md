# NoSQL Demo

FastAPI application with MongoDB and Redis (NoSQL stores). MongoDB is seeded from the university schema (database/sql/DDL.sql, DML.sql).

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (or pip)
- Docker & Docker Compose

## How to Run

1. **Start MongoDB and Redis**

   ```bash
   docker compose up -d
   ```

   MongoDB runs on `localhost:27017` (admin / password). Redis runs on `localhost:6379`.

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Seed the database**

   ```bash
   uv run python -m database.mongodb.seed
   ```

   Creates the `university` database, collections, indexes, and sample data. **Warning:** seed drops the database first (destructive, re-runnable).

4. **Start the API**

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

| Variable       | Default                              | Description              |
|----------------|--------------------------------------|--------------------------|
| `MONGO_URI`    | `mongodb://admin:password@localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME`| `university`                         | Database name            |
| `REDIS_URL`    | `redis://localhost:6379/0`           | Redis connection URL     |

The FastAPI app uses these. The seed script uses `database/mongodb/seed.py` and its own hardcoded connection string.

## How to Make Changes

| What to change | Where |
|----------------|-------|
| **API routes** | `app/routes/mongodb.py` (MongoDB), `app/routes/redis.py` (Redis) |
| **Request/response models** | `app/schema.py` |
| **Database connection** | `app/database.py`, `config.py` |
| **MongoDB schema & seed data** | `database/mongodb/seed.py` |
| **SQL schema (reference)** | `database/sql/DDL.sql`, `database/sql/DML.sql` |
| **Add new routers** | `app/main.py` — import and `app.include_router(...)` |

**Development workflow:** Run the API with `--reload` so changes apply automatically. Re-run the seed script after changing `database/mongodb/seed.py`.

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

Use the interactive API docs at http://localhost:8000/docs to try endpoints.
