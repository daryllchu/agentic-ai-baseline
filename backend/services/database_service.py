from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Employee
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations with proper session management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def upsert_employees(self, employees_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk upsert employee records with proper transaction handling"""
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        try:
            for emp_data in employees_data:
                try:
                    result = self._upsert_single_employee(emp_data)
                    if result['action'] == 'created':
                        created_count += 1
                    elif result['action'] == 'updated':
                        updated_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Employee {emp_data.get('employee_id', 'unknown')}: {str(e)}")
                    logger.error(f"Failed to upsert employee: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': errors
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during bulk upsert: {str(e)}")
            return {
                'success': False,
                'error': f"Database error: {str(e)}"
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during bulk upsert: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def _upsert_single_employee(self, emp_data: Dict[str, Any]) -> Dict[str, str]:
        """Upsert single employee record"""
        # Validate required fields
        required_fields = ['employee_id', 'data_source_id']
        for field in required_fields:
            if field not in emp_data:
                raise ValueError(f"Missing required field: {field}")
        
        employee_id = emp_data['employee_id']
        data_source_id = emp_data['data_source_id']
        
        # Check for existing employee
        existing = self.db.query(Employee).filter(
            Employee.employee_id == employee_id,
            Employee.data_source_id == data_source_id
        ).first()
        
        if existing:
            # Update existing employee
            for key, value in emp_data.items():
                if key not in ['created_at']:  # Don't update created_at
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            return {'action': 'updated', 'employee_id': employee_id}
        else:
            # Create new employee
            employee = Employee(**emp_data)
            self.db.add(employee)
            return {'action': 'created', 'employee_id': employee_id}
    
    def get_employee_by_id(self, employee_id: str, data_source_id: int) -> Optional[Employee]:
        """Get employee by ID and data source"""
        try:
            return self.db.query(Employee).filter(
                Employee.employee_id == employee_id,
                Employee.data_source_id == data_source_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting employee: {str(e)}")
            return None
    
    def get_employees_by_data_source(self, data_source_id: int, limit: int = 100, offset: int = 0) -> List[Employee]:
        """Get employees by data source with pagination"""
        try:
            return self.db.query(Employee).filter(
                Employee.data_source_id == data_source_id
            ).offset(offset).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting employees: {str(e)}")
            return []
    
    def count_employees_by_data_source(self, data_source_id: int) -> int:
        """Count employees by data source"""
        try:
            return self.db.query(Employee).filter(
                Employee.data_source_id == data_source_id
            ).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error counting employees: {str(e)}")
            return 0
    
    def delete_employees_by_data_source(self, data_source_id: int) -> int:
        """Delete all employees for a data source"""
        try:
            count = self.db.query(Employee).filter(
                Employee.data_source_id == data_source_id
            ).delete()
            self.db.commit()
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting employees: {str(e)}")
            return 0
    
    def close(self):
        """Close database session"""
        try:
            self.db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {str(e)}")