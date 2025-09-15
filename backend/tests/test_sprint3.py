import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
from main import app
from models import DataSource, Employee
from services.xml_parser import WorkdayXMLParser
from services.data_transformer import DataTransformer
from services.database_service import DatabaseService

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sprint3.db"
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
        "name": "Test Workday Sprint3",
        "type": "workday",
        "description": "Test data source for Sprint 3"
    })
    assert response.status_code == 200
    return response.json()

def test_workday_xml_parser():
    """Test Workday XML parser with secure parsing"""
    parser = WorkdayXMLParser()
    
    xml_content = b"""<?xml version="1.0"?>
    <wd:Report_Data xmlns:wd="urn:com.workday.report/HR_Employee_Export">
        <wd:Employee>
            <wd:Employee_ID>EMP001</wd:Employee_ID>
            <wd:First_Name>John</wd:First_Name>
            <wd:Last_Name>Doe</wd:Last_Name>
            <wd:Email_Address>john.doe@company.com</wd:Email_Address>
            <wd:Department>Engineering</wd:Department>
        </wd:Employee>
        <wd:Employee>
            <wd:Employee_ID>EMP002</wd:Employee_ID>
            <wd:First_Name>Jane</wd:First_Name>
            <wd:Last_Name>Smith</wd:Last_Name>
        </wd:Employee>
    </wd:Report_Data>"""
    
    result = parser.parse_xml_content(xml_content)
    
    assert result["success"] is True
    assert result["employee_count"] == 2
    assert len(result["employees"]) == 2
    
    # Check first employee
    emp1 = result["employees"][0]
    assert emp1["employee_id"] == "EMP001"
    assert emp1["first_name"] == "John"
    assert emp1["last_name"] == "Doe"
    assert emp1["email"] == "john.doe@company.com"
    assert emp1["department"] == "Engineering"

def test_data_transformer():
    """Test data transformation and validation"""
    transformer = DataTransformer()
    
    raw_data = {
        "employee_id": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@company.com",
        "department": "Engineering",
        "hire_date": "2023-01-15",
        "salary": "95000"
    }
    
    result = transformer.transform_employee_data(raw_data, 1)
    
    assert "error" not in result
    assert result["employee_id"] == "EMP001"
    assert result["first_name"] == "John"
    assert result["email"] == "john.doe@company.com"
    assert result["hire_date"] == "2023-01-15"
    assert result["salary"] == 95000.0
    assert result["data_source_id"] == 1

def test_data_transformer_validation():
    """Test data validation in transformer"""
    transformer = DataTransformer()
    
    # Test missing required fields
    invalid_data = {
        "first_name": "John",
        "email": "invalid-email"
    }
    
    result = transformer.transform_employee_data(invalid_data, 1)
    assert "error" in result
    assert "employee_id is required" in result["error"]

def test_data_transformer_email_validation():
    """Test email validation"""
    transformer = DataTransformer()
    
    # Valid email
    assert transformer._validate_email("test@example.com") == "test@example.com"
    
    # Invalid emails
    assert transformer._validate_email("invalid-email") == ""
    assert transformer._validate_email("") == ""

def test_data_transformer_date_parsing():
    """Test date parsing and standardization"""
    transformer = DataTransformer()
    
    # Test various date formats
    assert transformer._parse_date("2023-01-15") == "2023-01-15"
    assert transformer._parse_date("01/15/2023") == "2023-01-15"
    assert transformer._parse_date("01-15-2023") == "2023-01-15"
    assert transformer._parse_date("invalid-date") is None
    assert transformer._parse_date("") is None

def test_duplicate_detection():
    """Test duplicate employee detection"""
    transformer = DataTransformer()
    
    employees = [
        {"employee_id": "EMP001", "first_name": "John"},
        {"employee_id": "EMP002", "first_name": "Jane"},
        {"employee_id": "EMP001", "first_name": "John Duplicate"}
    ]
    
    duplicates = transformer.detect_duplicates(employees)
    
    assert "EMP001" in duplicates
    assert duplicates["EMP001"] == [0, 2]
    assert "EMP002" not in duplicates

def test_database_service_upsert():
    """Test database service upsert functionality"""
    db = TestingSessionLocal()
    
    try:
        # Create test data source
        data_source = DataSource(
            name="Test Source",
            type="workday",
            is_active=True
        )
        db.add(data_source)
        db.commit()
        db.refresh(data_source)
        
        db_service = DatabaseService(db)
        
        # Test data
        employees_data = [
            {
                "data_source_id": data_source.id,
                "employee_id": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "department": "Engineering",
                "status": "Active"
            },
            {
                "data_source_id": data_source.id,
                "employee_id": "EMP002",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "department": "Marketing",
                "status": "Active"
            }
        ]
        
        # First upsert - should create
        result = db_service.upsert_employees(employees_data)
        
        assert result["success"] is True
        assert result["created"] == 2
        assert result["updated"] == 0
        
        # Second upsert - should update
        employees_data[0]["department"] = "Updated Engineering"
        result = db_service.upsert_employees(employees_data)
        
        assert result["success"] is True
        assert result["created"] == 0
        assert result["updated"] == 2
        
    finally:
        db.close()

def test_employee_api_list(client, test_data_source):
    """Test employee listing API"""
    # First create some test employees directly in database
    db = TestingSessionLocal()
    try:
        employees = [
            Employee(
                data_source_id=test_data_source["id"],
                employee_id="EMP001",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                department="Engineering",
                status="Active"
            ),
            Employee(
                data_source_id=test_data_source["id"],
                employee_id="EMP002",
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                department="Marketing",
                status="Active"
            )
        ]
        
        for emp in employees:
            db.add(emp)
        db.commit()
        
    finally:
        db.close()
    
    # Test API
    response = client.get("/api/employees/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["employees"]) == 2
    assert data["pagination"]["total"] == 2

def test_employee_api_search(client, test_data_source):
    """Test employee search functionality"""
    # Create test employee
    db = TestingSessionLocal()
    try:
        employee = Employee(
            data_source_id=test_data_source["id"],
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department="Engineering",
            status="Active"
        )
        db.add(employee)
        db.commit()
    finally:
        db.close()
    
    # Test search by name
    response = client.get("/api/employees/?search=John")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "John"

def test_employee_api_stats(client, test_data_source):
    """Test employee statistics API"""
    response = client.get("/api/employees/stats/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_employees" in data
    assert "active_employees" in data
    assert "departments" in data