from fastapi import APIRouter, Depends, HTTPException, Query

from pymongo.collection import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.schema import EnrollmentAdd, EnrollmentRemove, StudentCreate, StudentUpdate

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


@router.get("/students")
def list_students(mongo_db=Depends(get_db)):
    """List all students from MongoDB."""
    students = list(mongo_db.student.find({}, {"_id": 0}))
    return {"students": students}


@router.get("/students/credits")
def list_students_with_aggregated_credits(mongo_db=Depends(get_db)):
    """List students with total credits aggregated from their enrolled courses."""
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "name": 1,
                "dept_name": 1,
                "total_credits": {"$sum": "$enrolled_courses.credits"},
            }
        }
    ]
    students = list(mongo_db.student_enrollments.aggregate(pipeline))
    return {"students": students}


@router.get("/students/credits/by-dept")
def list_students_with_aggregated_credits_by_dept(
    dept_name: str = Query(..., description="Department name to filter by"),
    mongo_db=Depends(get_db),
):
    """List students with total credits aggregated from their enrolled courses, filtered by department."""
    pipeline = [
        {"$match": {"dept_name": dept_name}},
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "name": 1,
                "dept_name": 1,
                "total_credits": {"$sum": "$enrolled_courses.credits"},
            }
        },
    ]
    students = list(mongo_db.student_enrollments.aggregate(pipeline))
    return {"students": students}


@router.post("/students")
def create_student(student: StudentCreate, mongo_db=Depends(get_db)):
    """Insert a new student."""
    doc = student.model_dump()
    try:
        mongo_db.student.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409, detail=f"Student '{student.id}' already exists"
        )
    return student.model_dump()


@router.put("/students/{student_id}")
def update_student(student_id: str, student: StudentUpdate, mongo_db=Depends(get_db)):
    """Update an existing student."""
    updates = {k: v for k, v in student.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update (name, dept_name, tot_cred)",
        )
    result = mongo_db.student.find_one_and_update(
        {"id": student_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return result


@router.delete("/students/{student_id}")
def delete_student(student_id: str, mongo_db=Depends(get_db)):
    """Delete a student."""
    result = mongo_db.student.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return {"message": f"Student '{student_id}' deleted"}


@router.get("/student_enrollments")
def list_student_enrollments(mongo_db=Depends(get_db)):
    """List all students with their enrolled courses."""
    enrollments = list(mongo_db.student_enrollments.find({}, {"_id": 0}))
    return {"student_enrollments": enrollments}


@router.post("/students/{student_id}/enrollments")
def add_enrollment(
    student_id: str, enrollment: EnrollmentAdd, mongo_db=Depends(get_db)
):
    """Add an enrollment to a student."""
    course = mongo_db.course.find_one({"course_id": enrollment.course_id}, {"_id": 0})
    if course is None:
        raise HTTPException(
            status_code=404, detail=f"Course '{enrollment.course_id}' not found"
        )
    student = mongo_db.student_enrollments.find_one({"id": student_id})
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    new_enrollment = {
        "course_id": enrollment.course_id,
        "title": course["title"],
        "credits": course["credits"],
        "dept_name": course["dept_name"],
        "sec_id": enrollment.sec_id,
        "semester": enrollment.semester,
        "year": enrollment.year,
        "grade": enrollment.grade,
    }
    existing = next(
        (
            e
            for e in student.get("enrolled_courses", [])
            if e["course_id"] == enrollment.course_id
            and e["sec_id"] == enrollment.sec_id
            and e["semester"] == enrollment.semester
            and e["year"] == enrollment.year
        ),
        None,
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Student already enrolled in {enrollment.course_id} sec {enrollment.sec_id} {enrollment.semester} {enrollment.year}",
        )
    result = mongo_db.student_enrollments.find_one_and_update(
        {"id": student_id},
        {"$push": {"enrolled_courses": new_enrollment}},
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )
    return result


@router.delete("/students/{student_id}/enrollments")
def remove_enrollment(
    student_id: str, enrollment: EnrollmentRemove, mongo_db=Depends(get_db)
):
    """Remove an enrollment from a student."""
    result = mongo_db.student_enrollments.find_one_and_update(
        {"id": student_id},
        {
            "$pull": {
                "enrolled_courses": {
                    "course_id": enrollment.course_id,
                    "sec_id": enrollment.sec_id,
                    "semester": enrollment.semester,
                    "year": enrollment.year,
                }
            }
        },
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return result
