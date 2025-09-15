from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from models import ETLJob
from services.encryption_service import EncryptionService
from pydantic import BaseModel

router = APIRouter(prefix="/api/files", tags=["File Viewer"])

class FileViewRequest(BaseModel):
    password: str

@router.post("/{job_id}/view")
def view_file_content(
    job_id: int, 
    request: FileViewRequest,
    db: Session = Depends(get_db)
):
    """View encrypted file content with password"""
    
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.encrypted_content or not job.content_salt:
        raise HTTPException(status_code=404, detail="No encrypted content available")
    
    try:
        # Decrypt file content
        decrypted_content = EncryptionService.decrypt_data(
            job.encrypted_content,
            job.content_salt,
            request.password
        )
        
        return {
            "job_id": job.id,
            "filename": job.file_path.split('/')[-1] if job.file_path else "unknown.xml",
            "content": decrypted_content,
            "source_type": job.source.type if job.source else "unknown"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid password")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to decrypt file content")