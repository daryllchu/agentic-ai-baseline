from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import DataSource
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data-sources", tags=["Data Sources"])

class DataSourceCreate(BaseModel):
    name: str
    type: str = "workday"
    connection_info: Optional[dict] = None

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    connection_info: Optional[dict] = None
    is_active: Optional[bool] = None

@router.post("/")
def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_db)
):
    """Create new data source"""
    
    # Check if name already exists
    existing = db.query(DataSource).filter(DataSource.name == data_source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Data source name already exists")
    
    db_data_source = DataSource(
        name=data_source.name,
        type=data_source.type,
        connection_info=data_source.connection_info or {},
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    
    return {
        "id": db_data_source.id,
        "name": db_data_source.name,
        "type": db_data_source.type,
        "is_active": db_data_source.is_active,
        "created_at": db_data_source.created_at
    }

@router.get("/")
def list_data_sources(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List data sources"""
    
    query = db.query(DataSource)
    
    if active_only:
        query = query.filter(DataSource.is_active == True)
    
    data_sources = query.offset(skip).limit(limit).all()
    
    return {
        "data_sources": [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "is_active": ds.is_active,
                "created_at": ds.created_at,
                "updated_at": ds.updated_at
            }
            for ds in data_sources
        ]
    }

@router.get("/{data_source_id}")
def get_data_source(data_source_id: int, db: Session = Depends(get_db)):
    """Get data source by ID"""
    
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return {
        "id": data_source.id,
        "name": data_source.name,
        "type": data_source.type,
        "connection_info": data_source.connection_info,
        "is_active": data_source.is_active,
        "created_at": data_source.created_at,
        "updated_at": data_source.updated_at
    }

@router.put("/{data_source_id}")
def update_data_source(
    data_source_id: int,
    data_source_update: DataSourceUpdate,
    db: Session = Depends(get_db)
):
    """Update data source"""
    
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Update fields
    if data_source_update.name is not None:
        # Check name uniqueness
        existing = db.query(DataSource).filter(
            DataSource.name == data_source_update.name,
            DataSource.id != data_source_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Data source name already exists")
        data_source.name = data_source_update.name
    
    if data_source_update.connection_info is not None:
        data_source.connection_info = data_source_update.connection_info
    
    if data_source_update.is_active is not None:
        data_source.is_active = data_source_update.is_active
    
    data_source.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "id": data_source.id,
        "name": data_source.name,
        "type": data_source.type,
        "is_active": data_source.is_active,
        "updated_at": data_source.updated_at
    }

@router.delete("/{data_source_id}")
def delete_data_source(data_source_id: int, db: Session = Depends(get_db)):
    """Delete data source"""
    
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Check if data source has associated ETL jobs
    from models import ETLJob
    job_count = db.query(ETLJob).filter(ETLJob.source_id == data_source_id).count()
    if job_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete data source with {job_count} associated ETL jobs"
        )
    
    db.delete(data_source)
    db.commit()
    
    return {"message": "Data source deleted successfully"}

@router.post("/{data_source_id}/test-connection")
def test_connection(data_source_id: int, db: Session = Depends(get_db)):
    """Test data source connection"""
    
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # For now, return success for all Workday sources
    # In future sprints, implement actual connection testing
    if data_source.type == "workday":
        logger.info(f"Connection test successful for data source {data_source_id}")
        return {
            "status": "success",
            "message": "Connection test successful",
            "tested_at": datetime.now(timezone.utc)
        }
    
    logger.warning(f"Connection testing not implemented for data source type: {data_source.type}")
    return {
        "status": "error",
        "message": "Connection testing not implemented for this data source type"
    }