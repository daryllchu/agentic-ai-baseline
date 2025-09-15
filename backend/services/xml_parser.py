from defusedxml import ElementTree as ET
from typing import Dict, List, Optional, Any
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WorkdayXMLParser:
    """Secure XML parser for Workday employee data"""
    
    def __init__(self):
        self.namespace_map = {
            'wd': 'urn:com.workday.report/HR_Employee_Export'
        }
        
    def parse_xml_content(self, xml_content: bytes) -> Dict[str, Any]:
        """Parse XML content and extract employee data"""
        try:
            # Use defusedxml to prevent XXE attacks
            root = ET.fromstring(xml_content)
            
            # Detect namespace
            namespace = self._detect_namespace(root)
            
            # Extract employees
            employees = self._extract_employees(root, namespace)
            
            return {
                "success": True,
                "employee_count": len(employees),
                "employees": employees,
                "namespace": namespace
            }
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {str(e)}")
            return {"success": False, "error": f"Invalid XML format: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected parsing error: {str(e)}")
            return {"success": False, "error": f"Parsing failed: {str(e)}"}
    
    def _detect_namespace(self, root) -> str:
        """Detect XML namespace prefix"""
        if root.tag.startswith('{'):
            return 'wd'
        elif 'wd:' in root.tag:
            return 'wd'
        return ''
    
    def _extract_employees(self, root, namespace: str) -> List[Dict[str, Any]]:
        """Extract employee data from XML"""
        employees = []
        
        # Find employee elements with namespace handling
        employee_xpath = './/wd:Employee' if namespace else './/Employee'
        employee_elements = root.findall(employee_xpath)
        
        if not employee_elements and namespace:
            # Fallback without namespace
            employee_elements = root.findall('.//Employee')
        
        for emp_elem in employee_elements:
            try:
                employee_data = self._extract_employee_data(emp_elem, namespace)
                if employee_data:
                    employees.append(employee_data)
            except Exception as e:
                logger.warning(f"Failed to extract employee data: {str(e)}")
                continue
        
        return employees
    
    def _extract_employee_data(self, emp_elem, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract individual employee data"""
        prefix = 'wd:' if namespace else ''
        
        # Core employee fields
        employee_data = {
            'employee_id': self._get_field_value(emp_elem, f'{prefix}Employee_ID'),
            'first_name': self._get_field_value(emp_elem, f'{prefix}First_Name'),
            'last_name': self._get_field_value(emp_elem, f'{prefix}Last_Name'),
            'email': self._get_field_value(emp_elem, f'{prefix}Email_Address'),
            'department': self._get_field_value(emp_elem, f'{prefix}Department'),
            'position': self._get_field_value(emp_elem, f'{prefix}Position_Title'),
            'hire_date': self._get_field_value(emp_elem, f'{prefix}Hire_Date'),
            'status': self._get_field_value(emp_elem, f'{prefix}Employee_Status', 'Active'),
            'manager_id': self._get_field_value(emp_elem, f'{prefix}Manager_ID'),
            'location': self._get_field_value(emp_elem, f'{prefix}Location'),
            'salary': self._get_field_value(emp_elem, f'{prefix}Salary')
        }
        
        # Validate required fields
        if not employee_data['employee_id']:
            logger.warning("Employee missing required employee_id")
            return None
            
        return employee_data
    
    def _get_field_value(self, element, xpath: str, default: str = "") -> str:
        """Safely extract field value from XML element"""
        try:
            found = element.find(xpath)
            if found is not None and found.text:
                return found.text.strip()
            
            # Try without namespace prefix as fallback
            if ':' in xpath:
                fallback_xpath = xpath.split(':', 1)[1]
                found = element.find(fallback_xpath)
                if found is not None and found.text:
                    return found.text.strip()
                    
            return default
        except Exception:
            return default