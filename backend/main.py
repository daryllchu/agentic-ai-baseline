from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import auth
import os
from routers import etl, data_sources
from jose import JWTError, jwt
from services.webhook_service import WebhookService
from datetime import datetime

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HR Data Exchange Hub API",
    description="""ETL platform for integrating employee data from multiple HR systems.
    
    ## Features
    * **Employee Data API** - Comprehensive employee data access with search, filtering, and export
    * **Field Mapping** - Configure data transformations between source and target systems
    * **ETL Processing** - Upload and process XML files from HR systems
    * **Data Quality** - Real-time data quality assessment and validation
    
    ## Authentication
    All endpoints require JWT authentication via HTTP-only cookies.
    
    ## Rate Limiting
    API endpoints are rate-limited to ensure fair usage and system stability.
    """,
    version="1.0.0",
    contact={
        "name": "HR Data Exchange Hub",
        "email": "support@hrdatahub.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "HR Data Exchange Hub API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hr-data-exchange-hub"}

@app.post("/api/auth/login")
async def login(credentials: auth.UserLogin, response: Response, db: Session = Depends(get_db)):
    # Accept any login for now
    access_token = auth.create_access_token(data={"sub": credentials.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=2592000  # 30 days
    )
    return {"user": {"email": credentials.email}}

@app.post("/api/auth/register")
async def register(user_data: auth.UserCreate, response: Response, db: Session = Depends(get_db)):
    try:
        existing_user = auth.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user = auth.create_user(db, user_data)
        access_token = auth.create_access_token(data={"sub": user.email})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=2592000  # 30 days
        )
        return {"user": {"email": user.email}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = auth.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {"email": user.email}

# Bearer token authentication for API access
def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        token_hash = payload.get("token_hash")
        
        if token_hash:
            # API token authentication
            from models import APIToken
            api_token = db.query(APIToken).filter(
                APIToken.token_hash == token_hash,
                APIToken.is_active == True
            ).first()
            
            if api_token:
                # Update last used timestamp
                api_token.last_used_at = datetime.utcnow()
                db.commit()
                return {"type": "api_token", "token_id": api_token.id}
        
        raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication dependency
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = auth.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Include routers
app.include_router(etl.router)
app.include_router(data_sources.router)
from routers import employees, mappings, docs, audit, public_auth, tokens, webhooks, file_viewer
app.include_router(employees.router)
app.include_router(mappings.router)
app.include_router(docs.router)
app.include_router(audit.router)
app.include_router(public_auth.router)
app.include_router(tokens.router)
app.include_router(webhooks.router)
app.include_router(file_viewer.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)