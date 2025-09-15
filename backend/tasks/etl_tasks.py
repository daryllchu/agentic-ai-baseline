from celery import current_task
from celery_app import celery_app
from sqlalchemy.orm import Session
from database import get_db
from models import ETLJob, Employee, EmployeeChangeLog
from services.xml_parser import WorkdayXMLParser
from services.sap_parser import SAPHCMParser
from services.data_transformer import DataTransformer
from services.database_service import DatabaseService
import boto3
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def validate_xml_file(self, file_key: str, job_id: int):
    """Validate XML file format and structure"""
    db = None
    try:
        # Update job status
        db = next(get_db())
        job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
        if not job:
            return {"status": "failed", "error": "Job not found"}
            
        job.status = "validating"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Process local sample file for development
        if 'local/' in file_key:
            # Read sample XML file directly
            sample_file_path = '/app/sample_data/workday_sample.xml'
            try:
                with open(sample_file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                # Parse XML and create employee records
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)
                
                # Determine source type and namespace based on root element
                if 'urn:sap.com:hcm:employee:export' in root.tag:
                    # SAP HCM format
                    ns = {'sap': 'urn:sap.com:hcm:employee:export'}
                    employees = root.findall('.//sap:Employee', ns)
                    source_type = 'sap_hcm'
                else:
                    # Workday format (default)
                    ns = {'wd': 'urn:com.workday.report/HR_Employee_Export'}
                    employees = root.findall('.//wd:Employee', ns)
                    source_type = 'workday'
                
                # Check for duplicates first
                employee_ids = []
                duplicates_found = []
                for emp_elem in employees:
                    if source_type == 'sap_hcm':
                        emp_id = emp_elem.find('sap:PersonnelNumber', ns).text if emp_elem.find('sap:PersonnelNumber', ns) is not None else None
                    else:
                        emp_id = emp_elem.find('wd:Employee_ID', ns).text if emp_elem.find('wd:Employee_ID', ns) is not None else None
                    
                    if emp_id:
                        if emp_id in employee_ids:
                            duplicates_found.append(emp_id)
                        else:
                            employee_ids.append(emp_id)
                
                if duplicates_found:
                    job.status = "failed"
                    job.error_details = f"Duplicate employee IDs found: {', '.join(set(duplicates_found))}"
                    db.commit()
                    return {"status": "failed", "error": f"Duplicate employee IDs found: {', '.join(set(duplicates_found))}"}
                
                # Extract and validate employee data using DataTransformer
                transformer = DataTransformer()
                raw_employees = []
                
                for emp_elem in employees:
                    # Extract employee data based on source type
                    if source_type == 'sap_hcm':
                        raw_data = {
                            'employee_id': emp_elem.find('sap:PersonnelNumber', ns).text if emp_elem.find('sap:PersonnelNumber', ns) is not None else None,
                            'first_name': emp_elem.find('sap:FirstName', ns).text if emp_elem.find('sap:FirstName', ns) is not None else None,
                            'last_name': emp_elem.find('sap:LastName', ns).text if emp_elem.find('sap:LastName', ns) is not None else None,
                            'email': emp_elem.find('sap:EmailAddress', ns).text if emp_elem.find('sap:EmailAddress', ns) is not None else None,
                            'department': emp_elem.find('sap:OrganizationalUnit', ns).text if emp_elem.find('sap:OrganizationalUnit', ns) is not None else None,
                            'position': emp_elem.find('sap:JobTitle', ns).text if emp_elem.find('sap:JobTitle', ns) is not None else None,
                            'hire_date': emp_elem.find('sap:HireDate', ns).text if emp_elem.find('sap:HireDate', ns) is not None else None,
                            'status': emp_elem.find('sap:EmployeeStatus', ns).text if emp_elem.find('sap:EmployeeStatus', ns) is not None else None,
                            'manager_id': emp_elem.find('sap:SupervisorNumber', ns).text if emp_elem.find('sap:SupervisorNumber', ns) is not None else None,
                            'salary': emp_elem.find('sap:Salary', ns).text if emp_elem.find('sap:Salary', ns) is not None else None
                        }
                    else:
                        # Workday format
                        raw_data = {
                            'employee_id': emp_elem.find('wd:Employee_ID', ns).text if emp_elem.find('wd:Employee_ID', ns) is not None else None,
                            'first_name': emp_elem.find('wd:First_Name', ns).text if emp_elem.find('wd:First_Name', ns) is not None else None,
                            'last_name': emp_elem.find('wd:Last_Name', ns).text if emp_elem.find('wd:Last_Name', ns) is not None else None,
                            'email': emp_elem.find('wd:Email_Address', ns).text if emp_elem.find('wd:Email_Address', ns) is not None else None,
                            'department': emp_elem.find('wd:Department', ns).text if emp_elem.find('wd:Department', ns) is not None else None,
                            'position': emp_elem.find('wd:Position_Title', ns).text if emp_elem.find('wd:Position_Title', ns) is not None else None,
                            'hire_date': emp_elem.find('wd:Hire_Date', ns).text if emp_elem.find('wd:Hire_Date', ns) is not None else None,
                            'status': emp_elem.find('wd:Employee_Status', ns).text if emp_elem.find('wd:Employee_Status', ns) is not None else None,
                            'manager_id': emp_elem.find('wd:Manager_ID', ns).text if emp_elem.find('wd:Manager_ID', ns) is not None else None,
                            'salary': emp_elem.find('wd:Salary', ns).text if emp_elem.find('wd:Salary', ns) is not None else None
                        }
                    
                    raw_employees.append(raw_data)
                
                # Transform and validate all employees
                transformed_employees = []
                validation_errors = []
                
                for raw_emp in raw_employees:
                    transformed = transformer.transform_employee_data(raw_emp, job.source_id)
                    if 'error' in transformed:
                        validation_errors.append(transformed['error'])
                    else:
                        transformed_employees.append(transformed)
                
                # Check for validation errors
                if validation_errors:
                    job.status = "failed"
                    job.error_details = f"Validation errors: {'; '.join(validation_errors[:3])}"  # Show first 3 errors
                    db.commit()
                    return {"status": "failed", "error": job.error_details}
                
                # Process validated employees with change detection
                processed_count = 0
                for emp_data in transformed_employees:
                    try:
                        # Check if employee already exists
                        existing = db.query(Employee).filter(
                            Employee.source_id == job.source_id,
                            Employee.employee_id == emp_data['employee_id']
                        ).first()
                        
                        if existing:
                            # Detect and log changes
                            changes = _detect_changes(existing, emp_data)
                            
                            # Update existing employee
                            existing.first_name = emp_data['first_name']
                            existing.last_name = emp_data['last_name']
                            existing.email = emp_data['email']
                            existing.department = emp_data['department']
                            existing.job_title = emp_data['position']
                            existing.hire_date = emp_data['hire_date']
                            existing.status = emp_data['status']
                            existing.manager_id = emp_data['manager_id']
                            existing.updated_at = datetime.now(timezone.utc)
                            
                            # Log changes
                            for change in changes:
                                change_log = EmployeeChangeLog(
                                    employee_id=existing.id,
                                    etl_job_id=job.id,
                                    field_name=change['field'],
                                    old_value=str(change['old_value']) if change['old_value'] is not None else None,
                                    new_value=str(change['new_value']) if change['new_value'] is not None else None,
                                    change_type='updated'
                                )
                                db.add(change_log)
                        else:
                            # Create new employee
                            new_employee = Employee(
                                source_id=job.source_id,
                                employee_id=emp_data['employee_id'],
                                first_name=emp_data['first_name'],
                                last_name=emp_data['last_name'],
                                email=emp_data['email'],
                                department=emp_data['department'],
                                job_title=emp_data['position'],
                                hire_date=emp_data['hire_date'],
                                status=emp_data['status'],
                                manager_id=emp_data['manager_id'],
                                created_at=datetime.now(timezone.utc),
                                updated_at=datetime.now(timezone.utc)
                            )
                            db.add(new_employee)
                            db.flush()  # Get the ID
                            
                            # Log creation
                            for field, value in emp_data.items():
                                if field not in ['data_source_id', 'created_at', 'updated_at'] and value is not None:
                                    change_log = EmployeeChangeLog(
                                        employee_id=new_employee.id,
                                        etl_job_id=job.id,
                                        field_name=field,
                                        old_value=None,
                                        new_value=str(value),
                                        change_type='created'
                                    )
                                    db.add(change_log)
                        
                        processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing employee: {str(e)}")
                        continue
                
                # Update job status
                job.status = "completed"
                job.records_processed = processed_count
                job.completed_at = datetime.now(timezone.utc)
                job.updated_at = datetime.now(timezone.utc)
                db.commit()
                
                return {"status": "completed", "employee_count": processed_count}
                
            except Exception as e:
                job.status = "failed"
                job.error_details = str(e)
                db.commit()
                return {"status": "failed", "error": str(e)}
        
        # S3 processing for production
        return {"status": "failed", "error": "S3 not configured for local development"}
            
    except Exception as e:
        logger.error(f"Validation task failed: {str(e)}")
        if db:
            try:
                job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    db.commit()
            except Exception:
                pass
        return {"status": "failed", "error": str(e)}
    finally:
        if db:
            db.close()

@celery_app.task(bind=True)
def process_xml_file(self, file_key: str, job_id: int, data_source_id: int):
    """Process XML file and extract employee data"""
    db = None
    db_service = None
    
    try:
        # Update job status
        db = next(get_db())
        db_service = DatabaseService(db)
        
        job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
        if not job:
            return {"status": "failed", "error": "Job not found"}
            
        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Download and parse XML
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET_NAME', 'hr-data-hub-files')
        
        response = s3.get_object(Bucket=bucket, Key=file_key)
        xml_content = response['Body'].read()
        
        # Parse XML
        parser = WorkdayXMLParser()
        parse_result = parser.parse_xml_content(xml_content)
        
        if not parse_result['success']:
            job.status = "failed"
            job.error_message = parse_result['error']
            db.commit()
            return {"status": "failed", "error": parse_result['error']}
        
        # Transform employee data
        transformer = DataTransformer()
        transformed_employees = []
        transformation_errors = []
        
        for raw_emp in parse_result['employees']:
            transformed = transformer.transform_employee_data(raw_emp, data_source_id)
            if 'error' in transformed:
                transformation_errors.append(transformed['error'])
            else:
                transformed_employees.append(transformed)
        
        # Detect duplicates
        duplicates = transformer.detect_duplicates(transformed_employees)
        if duplicates:
            logger.warning(f"Found duplicates: {duplicates}")
        
        # Bulk upsert to database
        if transformed_employees:
            upsert_result = db_service.upsert_employees(transformed_employees)
            
            if upsert_result['success']:
                job.status = "completed"
                job.processed_records = upsert_result['created'] + upsert_result['updated']
                job.completed_at = datetime.now(timezone.utc)
                
                if transformation_errors or upsert_result['errors'] > 0:
                    job.error_message = f"Partial success. Transformation errors: {len(transformation_errors)}, DB errors: {upsert_result['errors']}"
            else:
                job.status = "failed"
                job.error_message = upsert_result['error']
        else:
            job.status = "failed"
            job.error_message = "No valid employee data found"
        
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        return {
            "status": job.status,
            "processed_count": job.processed_records,
            "total_count": len(parse_result['employees']),
            "transformation_errors": len(transformation_errors),
            "duplicates_found": len(duplicates)
        }
        
    except Exception as e:
        logger.error(f"Processing task failed: {str(e)}")
        if db:
            try:
                job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                pass
        return {"status": "failed", "error": str(e)}
    finally:
        if db_service:
            db_service.close()
        elif db:
            db.close()

def _detect_changes(existing_employee, new_data):
    """Detect changes between existing employee and new data"""
    changes = []
    field_mapping = {
        'first_name': 'first_name',
        'last_name': 'last_name', 
        'email': 'email',
        'department': 'department',
        'job_title': 'position',
        'hire_date': 'hire_date',
        'status': 'status',
        'manager_id': 'manager_id'
    }
    
    for db_field, data_field in field_mapping.items():
        old_value = getattr(existing_employee, db_field)
        new_value = new_data.get(data_field)
        
        # Convert for comparison
        if old_value != new_value:
            changes.append({
                'field': db_field,
                'old_value': old_value,
                'new_value': new_value
            })
    
    return changes

# Legacy function removed - functionality moved to WorkdayXMLParser and DataTransformer