from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Webhook
from pydantic import BaseModel
import json
import secrets
from datetime import datetime, timezone
from typing import List, Optional

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[str]  # ['employee.created', 'employee.updated', 'employee.deleted']

class WebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    events: List[str]
    is_active: bool
    secret: str
    created_at: datetime

@router.get("/")
def list_webhooks(db: Session = Depends(get_db)):
    """List all webhooks"""
    webhooks = db.query(Webhook).all()
    return {
        "webhooks": [
            {
                "id": webhook.id,
                "name": webhook.name,
                "url": webhook.url,
                "events": json.loads(webhook.events) if webhook.events else [],
                "is_active": webhook.is_active,
                "created_at": webhook.created_at
            }
            for webhook in webhooks
        ]
    }

@router.post("/")
def create_webhook(webhook_data: WebhookCreate, db: Session = Depends(get_db)):
    """Create a new webhook"""
    secret = secrets.token_urlsafe(32)
    
    db_webhook = Webhook(
        name=webhook_data.name,
        url=webhook_data.url,
        events=json.dumps(webhook_data.events),
        secret=secret,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    return {
        "id": db_webhook.id,
        "name": db_webhook.name,
        "url": db_webhook.url,
        "events": webhook_data.events,
        "is_active": db_webhook.is_active,
        "secret": secret,
        "created_at": db_webhook.created_at
    }

@router.patch("/{webhook_id}")
def update_webhook_status(webhook_id: int, webhook_data: dict, db: Session = Depends(get_db)):
    """Update webhook status"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if 'is_active' in webhook_data:
        webhook.is_active = webhook_data['is_active']
    
    db.commit()
    
    return {"message": f"Webhook {'activated' if webhook.is_active else 'deactivated'}"}

@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """Delete a webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()
    
    return {"message": "Webhook deleted"}