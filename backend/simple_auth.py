from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

SECRET_KEY = "simple-secret-key"

@app.post("/api/auth/login")
async def login(credentials: LoginRequest, response: Response):
    # Simple hardcoded login
    if credentials.email == "admin@test.com" and credentials.password == "admin":
        token = jwt.encode(
            {"sub": credentials.email, "exp": datetime.utcnow() + timedelta(hours=24)}, 
            SECRET_KEY, 
            algorithm="HS256"
        )
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400
        )
        return {"user": {"email": credentials.email}}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)