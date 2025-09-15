from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import APIToken
from pydantic import BaseModel
import auth
import hashlib
import secrets
from datetime import datetime, timedelta

# Import authentication function from main
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    user = auth.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    return user

router = APIRouter(prefix="/api/tokens", tags=["API Tokens"])

class TokenCreate(BaseModel):
    name: str
    expires_days: int = 365

class TokenResponse(BaseModel):
    id: int
    name: str
    token: str
    expires_at: str

@router.post("/", response_model=TokenResponse)
def create_api_token(
    token_data: TokenCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    """Create a new API token"""
    
    # Generate random token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    # Create JWT token with long expiration
    expires_at = datetime.utcnow() + timedelta(days=token_data.expires_days)
    jwt_token = auth.create_access_token(
        data={"sub": "api_token", "token_hash": token_hash},
        expires_delta=timedelta(days=token_data.expires_days)
    )
    
    # Store token info in database
    api_token = APIToken(
        name=token_data.name,
        token_hash=token_hash,
        expires_at=expires_at
    )
    
    db.add(api_token)
    db.commit()
    db.refresh(api_token)
    
    return TokenResponse(
        id=api_token.id,
        name=api_token.name,
        token=jwt_token,
        expires_at=expires_at.isoformat()
    )

@router.get("/")
def list_api_tokens(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user_from_cookie)):
    """List all API tokens"""
    
    tokens = db.query(APIToken).all()
    
    return {
        "tokens": [
            {
                "id": token.id,
                "name": token.name,
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
                "is_active": token.is_active
            }
            for token in tokens
        ]
    }

@router.patch("/{token_id}")
def update_api_token(token_id: int, update_data: dict, request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user_from_cookie)):
    """Update API token status"""
    
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if 'is_active' in update_data:
        token.is_active = update_data['is_active']
    
    db.commit()
    
    return {"message": "Token updated successfully"}

@router.delete("/{token_id}")
def revoke_api_token(token_id: int, request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user_from_cookie)):
    """Revoke an API token"""
    
    token = db.query(APIToken).filter(APIToken.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    token.is_active = False
    db.commit()
    
    return {"message": "Token revoked successfully"}