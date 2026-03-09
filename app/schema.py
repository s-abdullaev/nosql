from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    dept_name: str
    building: str
    budget: float


class DepartmentUpdate(BaseModel):
    building: str | None = None
    budget: float | None = None
