from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, desc, asc
from database import get_db
from models import Employee
from typing import List, Optional
import logging
import csv
import io
import json
from datetime import datetime, date
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from main import verify_api_token

security = HTTPBearer()

# Cookie-based authentication for frontend
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    import auth
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    user = auth.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    return user

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.get("/")
def list_employees(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List employees with pagination"""
    
    try:
        total_count = db.query(Employee).count()
        employees = db.query(Employee).offset(skip).limit(limit).all()
        
        return {
            "employees": [
                {
                    "id": emp.id,
                    "employee_id": emp.employee_id or "",
                    "first_name": emp.first_name or "",
                    "last_name": emp.last_name or "",
                    "email": emp.email or "",
                    "department": emp.department or "",
                    "job_title": emp.job_title or "",
                    "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                    "status": emp.status or "",
                    "manager_id": emp.manager_id or "",
                    "data_source_id": emp.source_id or 0,
                    "created_at": emp.created_at.isoformat() if emp.created_at else None,
                    "updated_at": emp.updated_at.isoformat() if emp.updated_at else None
                }
                for emp in employees
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
    except Exception as e:
        return {
            "employees": [],
            "pagination": {
                "skip": 0,
                "limit": 25,
                "total": 0,
                "has_more": False
            }
        }

@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get employee by ID"""
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "id": employee.id,
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "department": employee.department,
        "job_title": employee.job_title,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
        "status": employee.status,
        "manager_id": employee.manager_id,
        "location": employee.location,
        "data_source_id": employee.source_id,
        "created_at": employee.created_at.isoformat() if employee.created_at else None,
        "updated_at": employee.updated_at.isoformat() if employee.updated_at else None
    }

@router.get("/stats/summary")
def get_employee_stats(
    data_source_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get employee statistics summary"""
    
    try:
        total_employees = db.query(Employee).count()
        active_employees = db.query(Employee).filter(Employee.status == "Active").count()
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": total_employees - active_employees,
            "departments": []
        }
    except Exception as e:
        return {
            "total_employees": 0,
            "active_employees": 0,
            "inactive_employees": 0,
            "departments": []
        }

@router.get("/search/advanced")
def advanced_search(
    request: Request,
    q: str = Query(..., min_length=2),
    fields: Optional[str] = Query(None, description="Comma-separated fields to search in"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Advanced search with field-specific queries and ranking"""
    
    search_fields = ['first_name', 'last_name', 'email', 'employee_id', 'job_title', 'department']
    if fields:
        requested_fields = [f.strip() for f in fields.split(',')]
        search_fields = [f for f in requested_fields if f in search_fields]
    
    search_term = f"%{q}%"
    conditions = []
    
    for field in search_fields:
        if hasattr(Employee, field):
            conditions.append(getattr(Employee, field).ilike(search_term))
    
    if not conditions:
        return {"employees": [], "pagination": {"skip": skip, "limit": limit, "total": 0}}
    
    query = db.query(Employee).filter(or_(*conditions))
    total_count = query.count()
    
    # Simple relevance scoring based on exact matches
    employees = query.offset(skip).limit(limit).all()
    
    results = []
    for emp in employees:
        score = 0
        # Calculate relevance score
        for field in search_fields:
            field_value = getattr(emp, field, '') or ''
            if q.lower() in field_value.lower():
                if field_value.lower().startswith(q.lower()):
                    score += 3  # Higher score for prefix matches
                else:
                    score += 1
        
        results.append({
            "id": emp.id,
            "employee_id": emp.employee_id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "department": emp.department,
            "job_title": emp.job_title,
            "status": emp.status,
            "relevance_score": score
        })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return {
        "employees": results,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total_count,
            "has_more": skip + limit < total_count
        },
        "search_info": {
            "query": q,
            "fields_searched": search_fields,
            "results_found": len(results)
        }
    }

@router.get("/export/csv")
def export_employees_csv(
    request: Request,
    department: Optional[str] = None,
    status: Optional[str] = None,
    fields: Optional[str] = Query(None, description="Comma-separated fields to export"),
    db: Session = Depends(get_db)
):
    """Export employees to CSV format"""
    
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.limit(10000).all()  # Limit for performance
    
    # Define available fields
    available_fields = {
        'employee_id': 'Employee ID',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        'department': 'Department',
        'job_title': 'Job Title',
        'hire_date': 'Hire Date',
        'status': 'Status',
        'manager_id': 'Manager ID',

    }
    
    # Select fields to export
    if fields:
        selected_fields = [f.strip() for f in fields.split(',') if f.strip() in available_fields]
    else:
        selected_fields = list(available_fields.keys())
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([available_fields[field] for field in selected_fields])
    
    # Write data
    for emp in employees:
        row = []
        for field in selected_fields:
            value = getattr(emp, field, '')
            if isinstance(value, (datetime, date)):
                value = value.isoformat() if value else ''
            row.append(str(value) if value is not None else '')
        writer.writerow(row)
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@router.get("/export/json")
def export_employees_json(
    request: Request,
    department: Optional[str] = None,
    status: Optional[str] = None,
    fields: Optional[str] = Query(None, description="Comma-separated fields to export"),
    db: Session = Depends(get_db)
):
    """Export employees to JSON format"""
    
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.limit(10000).all()
    
    # Define exportable fields
    available_fields = ['employee_id', 'first_name', 'last_name', 'email', 'department', 
                       'job_title', 'hire_date', 'status', 'manager_id']
    
    if fields:
        selected_fields = [f.strip() for f in fields.split(',') if f.strip() in available_fields]
    else:
        selected_fields = available_fields
    
    # Build export data
    export_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(employees),
            "fields_exported": selected_fields
        },
        "employees": []
    }
    
    for emp in employees:
        emp_data = {}
        for field in selected_fields:
            value = getattr(emp, field, None)
            if isinstance(value, (datetime, date)):
                value = value.isoformat() if value else None
            emp_data[field] = value
        export_data["employees"].append(emp_data)
    
    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
    )