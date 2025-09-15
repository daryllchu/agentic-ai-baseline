import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
from main import app
from models import DataSource, ETLJob
import tempfile
import os

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_etl.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_data_source(client):
    """Create test data source"""
    response = client.post("/api/data-sources/", json={
        "name": "Test Workday",
        "type": "workday",
        "description": "Test data source"
    })
    return response.json()

def test_create_data_source(client):
    """Test creating a data source"""
    response = client.post("/api/data-sources/", json={
        "name": "Test Workday",
        "type": "workday",
        "description": "Test data source for ETL"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workday"
    assert data["type"] == "workday"
    assert data["is_active"] == True

def test_list_data_sources(client, test_data_source):
    """Test listing data sources"""
    response = client.get("/api/data-sources/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data_sources"]) == 1
    assert data["data_sources"][0]["name"] == "Test Workday"

def test_get_data_source(client, test_data_source):
    """Test getting specific data source"""
    data_source_id = test_data_source["id"]
    response = client.get(f"/api/data-sources/{data_source_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == data_source_id
    assert data["name"] == "Test Workday"

def test_update_data_source(client, test_data_source):
    """Test updating data source"""
    data_source_id = test_data_source["id"]
    response = client.put(f"/api/data-sources/{data_source_id}", json={
        "description": "Updated description",
        "is_active": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False

def test_test_connection(client, test_data_source):
    """Test data source connection testing"""
    data_source_id = test_data_source["id"]
    response = client.post(f"/api/data-sources/{data_source_id}/test-connection")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_upload_xml_file_validation():
    """Test XML file validation"""
    from services.file_service import FileService
    from fastapi import UploadFile
    import io
    
    file_service = FileService()
    
    # Test valid XML
    valid_xml = """<?xml version="1.0"?>
    <wd:Report_Data>
        <wd:Employee>
            <wd:Employee_ID>12345</wd:Employee_ID>
            <wd:First_Name>John</wd:First_Name>
            <wd:Last_Name>Doe</wd:Last_Name>
        </wd:Employee>
    </wd:Report_Data>"""
    
    file_obj = io.BytesIO(valid_xml.encode())
    upload_file = UploadFile(filename="test.xml", file=file_obj)
    upload_file.size = len(valid_xml.encode())
    
    result = file_service.validate_xml_file(upload_file)
    assert result["valid"] == True
    assert result["employee_count"] == 1

def test_upload_xml_file_invalid_format():
    """Test XML file validation with invalid format"""
    from services.file_service import FileService
    from fastapi import UploadFile, HTTPException
    import io
    
    file_service = FileService()
    
    # Test invalid XML
    invalid_xml = "This is not XML"
    
    file_obj = io.BytesIO(invalid_xml.encode())
    upload_file = UploadFile(filename="test.xml", file=file_obj)
    upload_file.size = len(invalid_xml.encode())
    
    with pytest.raises(HTTPException) as exc_info:
        file_service.validate_xml_file(upload_file)
    
    assert exc_info.value.status_code == 400
    assert "Invalid XML format" in str(exc_info.value.detail)

def test_upload_xml_file_wrong_extension():
    """Test file validation with wrong extension"""
    from services.file_service import FileService
    from fastapi import UploadFile, HTTPException
    import io
    
    file_service = FileService()
    
    file_obj = io.BytesIO(b"content")
    upload_file = UploadFile(filename="test.txt", file=file_obj)
    
    with pytest.raises(HTTPException) as exc_info:
        file_service.validate_xml_file(upload_file)
    
    assert exc_info.value.status_code == 400
    assert "File must be XML format" in str(exc_info.value.detail)

def test_extract_employee_data():
    """Test employee data extraction from XML"""
    from tasks.etl_tasks import extract_employee_data
    import xml.etree.ElementTree as ET
    
    xml_data = """
    <wd:Employee>
        <wd:Employee_ID>12345</wd:Employee_ID>
        <wd:First_Name>John</wd:First_Name>
        <wd:Last_Name>Doe</wd:Last_Name>
        <wd:Email_Address>john.doe@company.com</wd:Email_Address>
        <wd:Department>Engineering</wd:Department>
        <wd:Position_Title>Software Engineer</wd:Position_Title>
        <wd:Hire_Date>2023-01-15</wd:Hire_Date>
    </wd:Employee>
    """
    
    element = ET.fromstring(xml_data)
    result = extract_employee_data(element)
    
    assert result["employee_id"] == "12345"
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["email"] == "john.doe@company.com"
    assert result["department"] == "Engineering"
    assert result["position"] == "Software Engineer"
    assert result["hire_date"] == "2023-01-15"
    assert result["status"] == "Active"

def test_list_etl_jobs(client):
    """Test listing ETL jobs"""
    response = client.get("/api/etl/jobs")
    
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)

def test_get_nonexistent_job(client):
    """Test getting non-existent ETL job"""
    response = client.get("/api/etl/jobs/999")
    
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]