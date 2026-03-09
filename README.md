# NoSQL Demo

FastAPI application with MongoDB and Redis (NoSQL stores). MongoDB is seeded from the university schema (database/sql/DDL.sql, DML.sql).

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (or pip)
- Docker & Docker Compose

## Running the Project

### 1. Start MongoDB and Redis

```bash
docker compose up -d
```

- **MongoDB** runs on `localhost:27017` with credentials `admin` / `password`.
- **Redis** runs on `localhost:6379`.

### 2. Install Dependencies

```bash
uv sync
```

### 3. Seed the Database

```bash
uv run python -m database.mongodb.seed
```

This creates the `university` database, collections, indexes, and sample data. **Warning:** `seed` drops the database first, so it is re-runnable but destructive.

### 4. Start the API

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

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

## Working with MongoDB

### Connect via mongosh

```bash
mongosh "mongodb://admin:password@localhost:27017"
```

### Collections (schema)

| Collection  | Description                          |
|-------------|--------------------------------------|
| `classroom` | Buildings and rooms                  |
| `department`| Departments and budgets              |
| `course`    | Courses and credits                  |
| `instructor`| Instructors and salaries             |
| `section`   | Course sections (semester, year)     |
| `teaches`   | Instructor–section assignments       |
| `student`   | Students and total credits           |
| `takes`     | Student enrollments and grades       |
| `advisor`   | Student–advisor links                |
| `time_slot` | Time slots                          |
| `prereq`    | Course prerequisites                |

### Example queries (mongosh)

```javascript
use university

// All departments
db.department.find()

// All Comp. Sci. courses
db.course.find({ dept_name: "Comp. Sci." })

// Students with more than 100 credits
db.student.find({ tot_cred: { $gt: 100 } })

// Sections in Fall 2017
db.section.find({ semester: "Fall", year: 2017 })
```

### Using PyMongo in Python

```python
from app.database import get_db

db = get_db()
departments = list(db.department.find({}, {"_id": 0}))
courses = list(db.course.find({"dept_name": "Comp. Sci."}))
```

### API Endpoints

| Endpoint    | Description              |
|-------------|--------------------------|
| `GET /`     | Hello message            |
| `GET /health` | Health check           |
| `GET /departments` | List all departments |

## Working with Redis

Redis provides key-value caching for string, integer, list, and JSON object values.

### Connect via redis-cli

```bash
redis-cli -h localhost -p 6379
```

### Redis API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /redis/string/{key}` | Set a string value (body: `{"value": "..."}`) |
| `GET /redis/string/{key}` | Get a string value |
| `POST /redis/int/{key}` | Set an integer value (body: `{"value": 123}`) |
| `GET /redis/int/{key}` | Get an integer value |
| `POST /redis/list/{key}/push` | Push a value onto the list (body: `{"value": "..."}` or `{"value": 123}` etc.) |
| `POST /redis/list/{key}/pop` | Pop a value from the end of the list |
| `GET /redis/list/{key}` | Get all values in the list |
| `POST /redis/json/{key}` | Set a JSON object (body: `{"value": {"a": 1}}`) |
| `GET /redis/json/{key}` | Get a JSON object value |

### Example usage

```bash
# Set and get a string
curl -X POST http://localhost:8000/redis/string/hello -H "Content-Type: application/json" -d '{"value": "world"}'
curl http://localhost:8000/redis/string/hello

# Set and get an integer
curl -X POST http://localhost:8000/redis/int/counter -H "Content-Type: application/json" -d '{"value": 42}'
curl http://localhost:8000/redis/int/counter

# Push and pop list values
curl -X POST http://localhost:8000/redis/list/items/push -H "Content-Type: application/json" -d '{"value": "a"}'
curl -X POST http://localhost:8000/redis/list/items/push -H "Content-Type: application/json" -d '{"value": 42}'
curl http://localhost:8000/redis/list/items
curl -X POST http://localhost:8000/redis/list/items/pop

# Set and get a JSON object
curl -X POST http://localhost:8000/redis/json/user -H "Content-Type: application/json" -d '{"value": {"name": "Alice", "age": 30}}'
curl http://localhost:8000/redis/json/user
```
