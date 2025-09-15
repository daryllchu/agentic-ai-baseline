from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import ETLJob, DataSource
from services.file_service import FileService
from services.encryption_service import EncryptionService
from tasks.etl_tasks import validate_xml_file, process_xml_file
from datetime import datetime, timezone
import pytz
from typing import List, Optional
import logging
import os
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/etl", tags=["ETL"])
file_service = FileService()

@router.post("/upload")
async def upload_xml_file(
    file: UploadFile = File(...),
    data_source_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Upload XML file and start ETL job"""
    
    # Validate data source exists
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Validate file format and size
    if not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="Only XML files are supported")
    
    # Check file size (limit to 50MB)
    file_content = await file.read()
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
    
    await file.seek(0)  # Reset file pointer
    
    # Secure filename to prevent path traversal
    secure_name = secure_filename(file.filename)
    if not secure_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Skip S3 upload for local development
    file_key = f"local/{data_source_id}/{secure_name}"
    
    try:
        # Read and encrypt file content
        file_content = await file.read()
        file_text = file_content.decode('utf-8')
        
        # Use a default password for encryption (in production, use user-provided password)
        encryption_password = "hr-data-secure-2024"
        encrypted_data = EncryptionService.encrypt_data(file_text, encryption_password)
        
        # Create ETL job record with encrypted content
        etl_job = ETLJob(
            source_id=data_source_id,
            file_path=file_key,
            status="uploaded",
            records_processed=0,
            records_failed=0,
            encrypted_content=encrypted_data['encrypted_data'],
            content_salt=encrypted_data['salt'],
            created_at=datetime.now(pytz.timezone('Asia/Singapore'))
        )
        
        db.add(etl_job)
        db.commit()
        db.refresh(etl_job)
        
        # Start validation task (will handle both Workday and SAP HCM formats)
        validate_task = validate_xml_file.delay(file_key, etl_job.id)
        
        db.commit()
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        logger.error(f"Failed to create ETL job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ETL job")
    
    return {
        "job_id": etl_job.id,
        "status": "uploaded",
        "message": "File uploaded successfully"
    }

@router.post("/jobs/{job_id}/process")
def start_processing(job_id: int, db: Session = Depends(get_db)):
    """Start processing validated XML file"""
    
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "validated":
        raise HTTPException(status_code=400, detail="Job must be validated before processing")
    
    try:
        # Start processing task
        process_task = process_xml_file.delay(job.file_path, job.id, job.source_id)
        
        # Update job status
        job.status = "processing"
        job.started_at = datetime.now(pytz.timezone('Asia/Singapore'))
        db.commit()
        
        logger.info(f"Started processing job {job.id} with task {process_task.id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to start processing job {job.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start processing")
    
    return {
        "job_id": job.id,
        "status": "processing",
        "message": "Processing started"
    }

@router.get("/jobs")
def list_jobs(
    skip: int = 0,
    limit: int = min(100, 1000),  # Cap at 1000
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List ETL jobs with optional filtering"""
    
    query = db.query(ETLJob)
    
    if status:
        query = query.filter(ETLJob.status == status)
    
    jobs = query.order_by(ETLJob.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "jobs": [
            {
                "id": job.id,
                "source_id": job.source_id,
                "file_path": job.file_path,
                "status": job.status,
                "records_processed": job.records_processed,
                "records_failed": job.records_failed,
                "created_at": job.created_at,
                "error_details": job.error_details
            }
            for job in jobs
        ]
    }

@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get ETL job details"""
    
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "source_id": job.source_id,
        "file_path": job.file_path,
        "status": job.status,
        "records_processed": job.records_processed,
        "records_failed": job.records_failed,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "error_details": job.error_details
    }

@router.get("/jobs/{job_id}/status")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get current job status and progress"""
    
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get Celery task status if available
    task_status = None
    task_progress = None
    
    if job.task_id:
        try:
            from celery_app import celery_app
            task = celery_app.AsyncResult(job.task_id)
            task_status = task.status
            
            if task.status == 'PROGRESS':
                task_progress = task.info
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            task_status = "unknown"
    
    return {
        "job_id": job.id,
        "status": job.status,
        "records_processed": job.records_processed,
        "records_failed": job.records_failed,
        "error_details": job.error_details
    }

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete ETL job and associated file"""
    
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    logger.info(f"Deleting job {job_id} with file {job.file_key}")
    
    # Delete file from S3
    if job.file_path:
        file_deleted = file_service.delete_file(job.file_path)
        if not file_deleted:
            logger.warning(f"Failed to delete file {job.file_path} from S3")
    
    # Delete job record
    db.delete(job)
    db.commit()
    
    logger.info(f"Successfully deleted job {job_id}")
    return {"message": "Job deleted successfully"}