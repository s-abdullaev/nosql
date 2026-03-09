from pydantic import BaseModel


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
