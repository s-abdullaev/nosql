from fastapi import APIRouter, Depends, HTTPException

from pymongo.collection import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.schema import DepartmentCreate, DepartmentUpdate

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


@router.get("/departments")
def list_departments(mongo_db=Depends(get_db)):
    """List all departments from MongoDB."""
    departments = list(mongo_db.department.find({}, {"_id": 0}))
    return {"departments": departments}


@router.post("/departments")
def create_department(department: DepartmentCreate, mongo_db=Depends(get_db)):
    """Insert a new department."""
    doc = department.model_dump()
    try:
        mongo_db.department.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"Department '{department.dept_name}' already exists")
    return department.model_dump()


@router.put("/departments/{dept_name}")
def update_department(dept_name: str, department: DepartmentUpdate, mongo_db=Depends(get_db)):
    """Update an existing department."""
    updates = {k: v for k, v in department.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update (building, budget)")
    result = mongo_db.department.find_one_and_update(
        {"dept_name": dept_name},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Department '{dept_name}' not found")
    return result


@router.delete("/departments/{dept_name}")
def delete_department(dept_name: str, mongo_db=Depends(get_db)):
    """Delete a department."""
    result = mongo_db.department.delete_one({"dept_name": dept_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Department '{dept_name}' not found")
    return {"message": f"Department '{dept_name}' deleted"}
