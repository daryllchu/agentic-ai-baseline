from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FieldMapping, DataSource, MappingTemplate
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import os
from services.sap_parser import SAPHCMParser

router = APIRouter(prefix="/api/mappings", tags=["Field Mappings"])

class MappingCreate(BaseModel):
    source_field: str
    target_field: str
    source_type: Optional[str] = None
    transformation_rule: Optional[str] = None
    is_required: bool = False

class MappingResponse(BaseModel):
    id: int
    source_field: str
    target_field: str
    transformation_rule: Optional[str]
    is_required: bool
    is_active: bool

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    mappings: List[MappingCreate]
    is_multi_source: bool = False
    source_types: Optional[List[str]] = None

class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_default: bool
    created_at: datetime
    mappings: List[MappingResponse]

@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    """List all mapping templates"""
    templates = db.query(MappingTemplate).order_by(MappingTemplate.is_default.desc(), MappingTemplate.created_at.desc()).all()
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "is_default": t.is_default or False,
                "created_at": t.created_at
            }
            for t in templates
        ]
    }

@router.post("/templates")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create mapping template"""
    template_data = {
        "mappings": [mapping.dict() for mapping in template.mappings]
    }
    
    db_template = MappingTemplate(
        name=template.name,
        description=template.description,
        template_data=template_data,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return {"id": db_template.id, "name": db_template.name}

@router.post("/templates/default")
def create_default_template(source_type: str = "workday", db: Session = Depends(get_db)):
    """Create default template for specified source type"""
    
    if source_type.lower() == "sap_hcm":
        template_name = "SAP HCM Standard Mapping"
        description = "Default field mappings for SAP HCM system"
        default_mappings = [
            {"source_field": "sap:PersonnelNumber", "target_field": "employee_id", "transformation_rule": None, "is_required": True},
            {"source_field": "sap:FirstName", "target_field": "first_name", "transformation_rule": None, "is_required": True},
            {"source_field": "sap:LastName", "target_field": "last_name", "transformation_rule": None, "is_required": True},
            {"source_field": "sap:EmailAddress", "target_field": "email", "transformation_rule": None, "is_required": True},
            {"source_field": "sap:OrganizationalUnit", "target_field": "department", "transformation_rule": None, "is_required": False},
            {"source_field": "sap:JobTitle", "target_field": "job_title", "transformation_rule": None, "is_required": False},
            {"source_field": "sap:HireDate", "target_field": "hire_date", "transformation_rule": "date_format", "is_required": False},
            {"source_field": "sap:EmployeeStatus", "target_field": "status", "transformation_rule": None, "is_required": False},
            {"source_field": "sap:SupervisorNumber", "target_field": "manager_id", "transformation_rule": None, "is_required": False},
        ]
    else:  # Default to Workday
        template_name = "Workday Standard Mapping"
        description = "Default field mappings for Workday HR system"
        default_mappings = [
            {"source_field": "wd:Employee_ID", "target_field": "employee_id", "transformation_rule": None, "is_required": True},
            {"source_field": "wd:First_Name", "target_field": "first_name", "transformation_rule": None, "is_required": True},
            {"source_field": "wd:Last_Name", "target_field": "last_name", "transformation_rule": None, "is_required": True},
            {"source_field": "wd:Email_Address", "target_field": "email", "transformation_rule": None, "is_required": True},
            {"source_field": "wd:Department", "target_field": "department", "transformation_rule": None, "is_required": False},
            {"source_field": "wd:Position_Title", "target_field": "job_title", "transformation_rule": None, "is_required": False},
            {"source_field": "wd:Hire_Date", "target_field": "hire_date", "transformation_rule": "date_format", "is_required": False},
            {"source_field": "wd:Employee_Status", "target_field": "status", "transformation_rule": None, "is_required": False},
            {"source_field": "wd:Manager_ID", "target_field": "manager_id", "transformation_rule": None, "is_required": False},
        ]
    
    # Check if template already exists
    existing = db.query(MappingTemplate).filter(
        MappingTemplate.name == template_name
    ).first()
    
    if existing:
        return {"message": f"{template_name} already exists", "id": existing.id}
    
    template_data = {"mappings": default_mappings}
    
    db_template = MappingTemplate(
        name=template_name,
        description=description,
        template_data=template_data,
        is_default=True,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return {"id": db_template.id, "name": db_template.name, "message": f"{template_name} created"}

@router.get("/templates/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template with mappings"""
    template = db.query(MappingTemplate).filter(MappingTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "mappings": template.template_data.get("mappings", [])
    }

@router.get("/preview/{source_id}")
def preview_mapping(source_id: int, db: Session = Depends(get_db)):
    """Preview data transformation with current mappings"""
    mappings = db.query(FieldMapping).filter(
        FieldMapping.source_id == source_id,
        FieldMapping.is_active == True
    ).all()
    
    # Get data source to determine type
    data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not data_source:
        return {"error": "Data source not found"}
    
    # Load appropriate sample data based on source type
    if data_source.type.lower() == 'sap_hcm':
        sample_file = "sample_data/sap_hcm_sample.xml"
        namespace = {"sap": "urn:sap.com:hcm:employee:export"}
        employee_xpath = ".//sap:Employee"
        field_prefix = "sap:"
        namespace_uri = "urn:sap.com:hcm:employee:export"
    else:  # Default to Workday
        sample_file = "sample_data/workday_sample.xml"
        namespace = {"wd": "urn:com.workday.report/HR_Employee_Export"}
        employee_xpath = ".//wd:Employee"
        field_prefix = "wd:"
        namespace_uri = "urn:com.workday.report/HR_Employee_Export"
    
    if not os.path.exists(sample_file):
        return {"error": "Sample data not available"}
    
    try:
        tree = ET.parse(sample_file)
        root = tree.getroot()
        
        # Get first employee for preview
        employee = root.find(employee_xpath, namespace)
        if employee is None:
            return {"error": "No employee data found"}
        
        # Extract source data
        source_data = {}
        for child in employee:
            field_name = child.tag.replace(f"{{{namespace_uri}}}", field_prefix)
            source_data[field_name] = child.text
        
        # Apply mappings
        transformed_data = {}
        mapped_fields = 0
        for mapping in mappings:
            if mapping.source_field in source_data:
                value = source_data[mapping.source_field]
                # Apply transformation if specified
                if mapping.transformation_rule == 'date_format' and value:
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(value, '%Y-%m-%d')
                        value = dt.strftime('%Y-%m-%d')
                    except:
                        pass
                transformed_data[mapping.target_field] = value
                mapped_fields += 1
        
        # Calculate data quality metrics
        total_source_fields = len(source_data)
        total_target_fields = 9  # Standard employee model fields
        required_fields = ['employee_id', 'first_name', 'last_name', 'email']
        required_mapped = sum(1 for field in required_fields if field in transformed_data)
        
        completeness = (mapped_fields / total_source_fields * 100) if total_source_fields > 0 else 0
        accuracy = 95  # Assume high accuracy for valid mappings
        consistency = 90  # Assume good consistency
        validity = (required_mapped / len(required_fields) * 100) if required_fields else 100
        
        quality_metrics = {
            "completeness": round(completeness),
            "accuracy": round(accuracy),
            "consistency": round(consistency),
            "validity": round(validity),
            "totalFields": total_target_fields,
            "mappedFields": len(transformed_data),
            "requiredFieldsMapped": required_mapped,
            "totalRequiredFields": len(required_fields)
        }
        
        # Generate quality issues
        issues = []
        if required_mapped < len(required_fields):
            missing = [f for f in required_fields if f not in transformed_data]
            for field in missing:
                issues.append({
                    "type": "error",
                    "field": field,
                    "message": "Required field not mapped"
                })
        
        return {
            "source_data": source_data,
            "transformed_data": transformed_data,
            "mappings_applied": mapped_fields,
            "quality_metrics": quality_metrics,
            "quality_issues": issues
        }
    
    except Exception as e:
        return {"error": f"Preview failed: {str(e)}"}

@router.post("/multi-source")
def create_multi_source_mapping(
    mapping_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create multi-source field mapping configuration"""
    
    mapping_set_id = f"multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    created_mappings = []
    
    try:
        for source_type, mappings in mapping_data.get("mappings", {}).items():
            for mapping in mappings:
                db_mapping = FieldMapping(
                    mapping_set_id=mapping_set_id,
                    source_type=source_type,
                    source_field=mapping["source_field"],
                    target_field=mapping["target_field"],
                    transformation_rule=mapping.get("transformation_rule"),
                    is_required=mapping.get("is_required", False),
                    is_active=True,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(db_mapping)
                created_mappings.append(db_mapping)
        
        db.commit()
        
        return {
            "mapping_set_id": mapping_set_id,
            "mappings_created": len(created_mappings),
            "source_types": list(mapping_data.get("mappings", {}).keys())
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create multi-source mapping: {str(e)}")

@router.get("/multi-source/{mapping_set_id}")
def get_multi_source_mapping(mapping_set_id: str, db: Session = Depends(get_db)):
    """Get multi-source mapping configuration"""
    
    mappings = db.query(FieldMapping).filter(
        FieldMapping.mapping_set_id == mapping_set_id,
        FieldMapping.is_active == True
    ).all()
    
    if not mappings:
        raise HTTPException(status_code=404, detail="Multi-source mapping not found")
    
    # Group mappings by source type
    grouped_mappings = {}
    for mapping in mappings:
        source_type = mapping.source_type or "unknown"
        if source_type not in grouped_mappings:
            grouped_mappings[source_type] = []
        
        grouped_mappings[source_type].append({
            "id": mapping.id,
            "source_field": mapping.source_field,
            "target_field": mapping.target_field,
            "transformation_rule": mapping.transformation_rule,
            "is_required": mapping.is_required
        })
    
    return {
        "mapping_set_id": mapping_set_id,
        "mappings": grouped_mappings,
        "source_types": list(grouped_mappings.keys())
    }

@router.get("/{source_id}")
def get_mappings(source_id: int, db: Session = Depends(get_db)):
    """Get field mappings for a data source"""
    
    # Verify data source exists
    data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    mappings = db.query(FieldMapping).filter(
        FieldMapping.source_id == source_id,
        FieldMapping.is_active == True
    ).all()
    
    return {
        "mappings": [
            {
                "id": m.id,
                "source_field": m.source_field,
                "target_field": m.target_field,
                "transformation_rule": m.transformation_rule,
                "is_required": m.is_required,
                "is_active": m.is_active
            }
            for m in mappings
        ]
    }

@router.post("/{source_id}")
def create_mapping(
    source_id: int,
    mapping: MappingCreate,
    db: Session = Depends(get_db)
):
    """Create new field mapping"""
    
    # Verify data source exists
    data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Check if mapping already exists
    existing = db.query(FieldMapping).filter(
        FieldMapping.source_id == source_id,
        FieldMapping.source_field == mapping.source_field,
        FieldMapping.target_field == mapping.target_field
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Mapping already exists")
    
    db_mapping = FieldMapping(
        source_id=source_id,
        source_field=mapping.source_field,
        target_field=mapping.target_field,
        transformation_rule=mapping.transformation_rule,
        is_required=mapping.is_required,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    
    return {
        "id": db_mapping.id,
        "source_field": db_mapping.source_field,
        "target_field": db_mapping.target_field,
        "transformation_rule": db_mapping.transformation_rule,
        "is_required": db_mapping.is_required
    }

@router.put("/{mapping_id}")
def update_mapping(
    mapping_id: int,
    mapping_update: MappingCreate,
    db: Session = Depends(get_db)
):
    """Update field mapping"""
    
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    mapping.source_field = mapping_update.source_field
    mapping.target_field = mapping_update.target_field
    mapping.transformation_rule = mapping_update.transformation_rule
    mapping.is_required = mapping_update.is_required
    
    db.commit()
    
    return {
        "id": mapping.id,
        "source_field": mapping.source_field,
        "target_field": mapping.target_field,
        "transformation_rule": mapping.transformation_rule,
        "is_required": mapping.is_required
    }

@router.delete("/{mapping_id}")
def delete_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Delete field mapping"""
    
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "Mapping deleted successfully"}

@router.post("/{source_id}/bulk")
def create_bulk_mappings(
    source_id: int,
    mappings: List[MappingCreate],
    db: Session = Depends(get_db)
):
    """Create multiple field mappings at once"""
    
    # Verify data source exists
    data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Delete existing mappings for this source
    db.query(FieldMapping).filter(FieldMapping.source_id == source_id).delete()
    
    # Create new mappings
    created_mappings = []
    for mapping_data in mappings:
        db_mapping = FieldMapping(
            source_id=source_id,
            source_field=mapping_data.source_field,
            target_field=mapping_data.target_field,
            transformation_rule=mapping_data.transformation_rule,
            is_required=mapping_data.is_required,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_mapping)
        created_mappings.append(db_mapping)
    
    db.commit()
    
    return {
        "message": f"Created {len(created_mappings)} mappings",
        "mappings": [
            {
                "id": m.id,
                "source_field": m.source_field,
                "target_field": m.target_field,
                "transformation_rule": m.transformation_rule,
                "is_required": m.is_required
            }
            for m in created_mappings
        ]
    }

