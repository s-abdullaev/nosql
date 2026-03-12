from pydantic import BaseModel


# ── MongoDB schemas ──────────────────────────────────────────────────────────


class StudentCreate(BaseModel):
    id: str
    name: str
    dept_name: str | None = None
    tot_cred: int = 0


class StudentUpdate(BaseModel):
    name: str | None = None
    dept_name: str | None = None
    tot_cred: int | None = None


class EnrollmentAdd(BaseModel):
    course_id: str
    sec_id: str
    semester: str
    year: int
    grade: str | None = None


class EnrollmentRemove(BaseModel):
    course_id: str
    sec_id: str
    semester: str
    year: int


# ── PostGIS schemas ──────────────────────────────────────────────────────────


class RestaurantCreate(BaseModel):
    name: str
    cuisine: str
    address: str
    latitude: float
    longitude: float


class RestaurantUpdate(BaseModel):
    name: str | None = None
    cuisine: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class RegionCreate(BaseModel):
    name: str
    description: str | None = None
    coordinates: list[list[float]]
    """Ring of [longitude, latitude] pairs forming the polygon boundary."""


class RegionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    coordinates: list[list[float]] | None = None


# ── Full-Text Search schemas ─────────────────────────────────────────────────


class ArticleResult(BaseModel):
    id: int
    title: str
    author: str
    category: str
    published: str
    rank: float | None = None
    snippet: str | None = None


class SearchResponse(BaseModel):
    query: str
    mode: str
    count: int
    results: list[ArticleResult]


class ArticleDetail(BaseModel):
    id: int
    title: str
    body: str
    author: str
    category: str
    published: str
