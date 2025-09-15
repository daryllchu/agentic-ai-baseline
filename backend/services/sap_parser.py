import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SAPHCMParser:
    """Parser for SAP HCM XML employee data"""
    
    def __init__(self):
        self.namespace = {"sap": "urn:sap.com:hcm:employee:export"}
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse SAP HCM XML file and extract employee data"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            employees = []
            for employee_elem in root.findall(".//sap:Employee", self.namespace):
                employee_data = self._extract_employee_data(employee_elem)
                if employee_data:
                    employees.append(employee_data)
            
            logger.info(f"Parsed {len(employees)} employees from SAP HCM file")
            return employees
            
        except Exception as e:
            logger.error(f"Error parsing SAP HCM file {file_path}: {str(e)}")
            raise
    
    def _extract_employee_data(self, employee_elem) -> Dict[str, Any]:
        """Extract individual employee data from XML element"""
        try:
            # Extract SAP HCM specific fields
            employee_data = {
                "personnel_number": self._get_text(employee_elem, "sap:PersonnelNumber"),
                "first_name": self._get_text(employee_elem, "sap:FirstName"),
                "last_name": self._get_text(employee_elem, "sap:LastName"),
                "email_address": self._get_text(employee_elem, "sap:EmailAddress"),
                "organizational_unit": self._get_text(employee_elem, "sap:OrganizationalUnit"),
                "job_title": self._get_text(employee_elem, "sap:JobTitle"),
                "hire_date": self._get_text(employee_elem, "sap:HireDate"),
                "employee_status": self._get_text(employee_elem, "sap:EmployeeStatus"),
                "supervisor_number": self._get_text(employee_elem, "sap:SupervisorNumber"),
                "cost_center": self._get_text(employee_elem, "sap:CostCenter"),
                "company_code": self._get_text(employee_elem, "sap:CompanyCode"),
            }
            
            return employee_data
            
        except Exception as e:
            logger.error(f"Error extracting employee data: {str(e)}")
            return None
    
    def _get_text(self, parent_elem, xpath: str) -> str:
        """Safely extract text from XML element"""
        elem = parent_elem.find(xpath, self.namespace)
        return elem.text.strip() if elem is not None and elem.text else ""
    
    def get_sample_fields(self) -> List[str]:
        """Get list of available SAP HCM fields for mapping"""
        return [
            "sap:PersonnelNumber",
            "sap:FirstName", 
            "sap:LastName",
            "sap:EmailAddress",
            "sap:OrganizationalUnit",
            "sap:JobTitle",
            "sap:HireDate",
            "sap:EmployeeStatus",
            "sap:SupervisorNumber",
            "sap:CostCenter",
            "sap:CompanyCode"
        ]