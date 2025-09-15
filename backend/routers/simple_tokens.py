from fastapi import APIRouter

router = APIRouter(prefix="/api/tokens", tags=["API Tokens"])

@router.get("/")
def list_tokens():
    return {"tokens": []}

@router.post("/")
def create_token(token_data: dict):
    return {"message": "Token created"}

@router.delete("/{token_id}")
def delete_token(token_id: int):
    return {"message": "Token deleted"}