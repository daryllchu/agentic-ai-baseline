from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import re
import logging

logger = logging.getLogger(__name__)

class DataTransformer:
    """Transform and validate employee data"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$'   # MM-DD-YYYY
        ]
    
    def transform_employee_data(self, raw_data: Dict[str, Any], data_source_id: int) -> Dict[str, Any]:
        """Transform raw employee data to standardized format"""
        try:
            transformed = {
                'data_source_id': data_source_id,
                'employee_id': self._clean_string(raw_data.get('employee_id', '')),
                'first_name': self._clean_string(raw_data.get('first_name', '')),
                'last_name': self._clean_string(raw_data.get('last_name', '')),
                'email': self._validate_email(raw_data.get('email', '')),
                'department': self._clean_string(raw_data.get('department', '')),
                'position': self._clean_string(raw_data.get('position', '')),
                'hire_date': self._parse_date(raw_data.get('hire_date', '')),
                'status': self._normalize_status(raw_data.get('status', 'Active')),
                'manager_id': self._clean_string(raw_data.get('manager_id', '')),
                'location': self._clean_string(raw_data.get('location', '')),
                'salary': self._parse_salary(raw_data.get('salary', '')),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Validate required fields
            validation_errors = self._validate_required_fields(transformed)
            if validation_errors:
                return {'error': f"Validation failed: {', '.join(validation_errors)}"}
            
            return transformed
            
        except Exception as e:
            logger.error(f"Data transformation error: {str(e)}")
            return {'error': f"Transformation failed: {str(e)}"}
    
    def _clean_string(self, value: str) -> str:
        """Clean and sanitize string values"""
        if not value:
            return ""
        
        # Remove extra whitespace and control characters
        cleaned = re.sub(r'\s+', ' ', str(value).strip())
        
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[<>"\']', '', cleaned)
        
        return cleaned[:255]  # Limit length
    
    def _validate_email(self, email: str) -> str:
        """Validate and clean email address"""
        if not email:
            return ""
        
        email = email.strip().lower()
        
        if self.email_pattern.match(email):
            return email
        
        logger.warning(f"Invalid email format: {email}")
        return ""
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse and standardize date format"""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try to match known patterns
        for pattern in self.date_patterns:
            if re.match(pattern, date_str):
                try:
                    # Convert to standard format YYYY-MM-DD
                    if '/' in date_str:
                        # MM/DD/YYYY format
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    elif '-' in date_str and len(date_str) == 10:
                        # Already in YYYY-MM-DD format
                        return date_str
                    elif '-' in date_str:
                        # MM-DD-YYYY format
                        parts = date_str.split('-')
                        if len(parts) == 3:
                            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                except Exception:
                    pass
        
        logger.warning(f"Invalid date format: {date_str}")
        return None
    
    def _normalize_status(self, status: str) -> str:
        """Normalize employee status"""
        if not status:
            return "Active"
        
        status = status.strip().lower()
        
        # Map common status variations
        status_map = {
            'active': 'Active',
            'inactive': 'Inactive',
            'terminated': 'Inactive',
            'on leave': 'On Leave',
            'leave': 'On Leave',
            'suspended': 'Suspended'
        }
        
        return status_map.get(status, 'Active')
    
    def _parse_salary(self, salary_str: str) -> Optional[float]:
        """Parse salary value"""
        if not salary_str:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', str(salary_str).strip())
        
        try:
            salary = float(cleaned)
            # Validate reasonable salary range
            if 0 <= salary <= 10000000:  # $0 to $10M
                return salary
        except ValueError:
            pass
        
        logger.warning(f"Invalid salary format: {salary_str}")
        return None
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate required fields"""
        errors = []
        
        if not data.get('employee_id'):
            errors.append("employee_id is required")
        
        if not data.get('first_name'):
            errors.append("first_name is required")
        
        if not data.get('last_name'):
            errors.append("last_name is required")
        
        return errors
    
    def detect_duplicates(self, employees: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Detect duplicate employees by employee_id"""
        duplicates = {}
        seen_ids = {}
        
        for idx, emp in enumerate(employees):
            emp_id = emp.get('employee_id')
            if emp_id:
                if emp_id in seen_ids:
                    if emp_id not in duplicates:
                        duplicates[emp_id] = [seen_ids[emp_id]]
                    duplicates[emp_id].append(idx)
                else:
                    seen_ids[emp_id] = idx
        
        return duplicates