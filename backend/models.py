from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

def singapore_now():
    return datetime.now(pytz.timezone('Asia/Singapore'))

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=singapore_now)
    
    users = relationship("User", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="users")
    
    __table_args__ = (Index('ix_tenant_email', 'tenant_id', 'email', unique=True),)

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # 'workday', 'bamboohr', etc.
    connection_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="source")
    field_mappings = relationship("FieldMapping", back_populates="source")
    etl_jobs = relationship("ETLJob", back_populates="source")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    employee_id = Column(String(50), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    department = Column(String(100))
    job_title = Column(String(100))
    manager_id = Column(String(50))
    hire_date = Column(Date)
    status = Column(String(20))
    raw_data = Column(JSON)  # Original XML data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    source = relationship("DataSource", back_populates="employees")
    change_logs = relationship("EmployeeChangeLog", back_populates="employee")

class FieldMapping(Base):
    __tablename__ = "field_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)  # Allow null for multi-source mappings
    mapping_set_id = Column(String(255), nullable=True)  # Group mappings together
    source_field = Column(String(255), nullable=False)
    target_field = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=True)  # 'workday', 'sap_hcm', etc.
    transformation_rule = Column(Text)
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source = relationship("DataSource", back_populates="field_mappings")

class MappingTemplate(Base):
    __tablename__ = "mapping_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_data = Column(JSON)  # Stores the mapping configuration
    is_default = Column(Boolean, default=False)
    is_multi_source = Column(Boolean, default=False)  # Supports multiple sources
    source_types = Column(JSON)  # List of supported source types
    created_at = Column(DateTime, default=datetime.utcnow)

class ETLJob(Base):
    __tablename__ = "etl_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    file_path = Column(String(500))
    status = Column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_details = Column(Text)
    encrypted_content = Column(Text)  # Encrypted file content
    content_salt = Column(String(255))  # Salt for encryption
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source = relationship("DataSource", back_populates="etl_jobs")

class EmployeeChangeLog(Base):
    __tablename__ = "employee_change_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    etl_job_id = Column(Integer, ForeignKey("etl_jobs.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    change_type = Column(String(20), nullable=False)  # 'created', 'updated'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="change_logs")
    etl_job = relationship("ETLJob")

class APIToken(Base):
    __tablename__ = "api_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(Text)  # JSON string of events to listen for
    is_active = Column(Boolean, default=True)
    secret = Column(String(255))  # For webhook signature verification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)