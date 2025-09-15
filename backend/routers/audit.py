from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import EmployeeChangeLog, Employee, ETLJob
from typing import Optional

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("/employee-changes/{employee_id}")
def get_employee_changes(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get change history for a specific employee"""
    changes = db.query(EmployeeChangeLog).filter(
        EmployeeChangeLog.employee_id == employee_id
    ).order_by(EmployeeChangeLog.created_at.desc()).all()
    
    return {
        "employee_id": employee_id,
        "changes": [
            {
                "id": change.id,
                "field_name": change.field_name,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "change_type": change.change_type,
                "created_at": change.created_at,
                "etl_job_id": change.etl_job_id
            }
            for change in changes
        ]
    }

@router.get("/changes")
def get_all_changes(
    limit: int = Query(50, le=100),
    skip: int = Query(0),
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all employee changes with pagination"""
    query = db.query(EmployeeChangeLog).join(Employee).join(ETLJob)
    
    if employee_id:
        query = query.filter(EmployeeChangeLog.employee_id == employee_id)
    
    changes = query.order_by(EmployeeChangeLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "changes": [
            {
                "id": change.id,
                "employee_id": change.employee_id,
                "employee_name": f"{change.employee.first_name} {change.employee.last_name}",
                "field_name": change.field_name,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "change_type": change.change_type,
                "created_at": change.created_at,
                "etl_job_id": change.etl_job_id
            }
            for change in changes
        ]
    }