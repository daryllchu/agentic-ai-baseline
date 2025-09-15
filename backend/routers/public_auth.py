from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import APIToken
from pydantic import BaseModel
import auth
import hashlib
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/public", tags=["Public Auth"])

class TokenRequest(BaseModel):
    email: str
    api_key: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Simple API key for demo - in production use proper authentication
VALID_API_KEYS = {
    "demo_key_123": "Demo Client",
    "workday_integration": "Workday System",
    "sap_connector": "SAP HCM System"
}

@router.post("/token", response_model=TokenResponse)
def request_api_token(
    request: TokenRequest,
    db: Session = Depends(get_db)
):
    """Request JWT token for external systems using API key"""
    
    # Validate API key
    if request.api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    client_name = VALID_API_KEYS[request.api_key]
    
    # Generate token hash
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    # Create JWT token (24 hours expiry for external requests)
    expires_delta = timedelta(hours=24)
    jwt_token = auth.create_access_token(
        data={"sub": "external_api", "token_hash": token_hash, "client": client_name},
        expires_delta=expires_delta
    )
    
    # Store token in database
    api_token = APIToken(
        name=f"{client_name} - {request.email}",
        token_hash=token_hash,
        expires_at=datetime.utcnow() + expires_delta
    )
    
    db.add(api_token)
    db.commit()
    
    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        expires_in=86400  # 24 hours in seconds
    )