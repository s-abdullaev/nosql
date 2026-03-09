# NoSQL Demo

FastAPI application with MongoDB, seeded from the university schema (database/sql/DDL.sql, DML.sql).

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (or pip)
- Docker & Docker Compose

## Running the Project

### 1. Start MongoDB

```bash
docker compose up -d
```

MongoDB runs on `localhost:27017` with credentials `admin` / `password`.

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
