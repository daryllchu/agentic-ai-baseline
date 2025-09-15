import requests
import json
import hashlib
import hmac
from sqlalchemy.orm import Session
from models import Webhook
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    @staticmethod
    def trigger_webhook(db: Session, event_type: str, data: Dict[Any, Any]):
        """Trigger webhooks for a specific event"""
        webhooks = db.query(Webhook).filter(
            Webhook.is_active == True
        ).all()
        
        for webhook in webhooks:
            try:
                events = json.loads(webhook.events) if webhook.events else []
                if event_type in events:
                    WebhookService._send_webhook(webhook, event_type, data)
            except Exception as e:
                logger.error(f"Error processing webhook {webhook.id}: {e}")
    
    @staticmethod
    def _send_webhook(webhook: Webhook, event_type: str, data: Dict[Any, Any]):
        """Send webhook HTTP request"""
        payload = {
            "event": event_type,
            "timestamp": data.get("timestamp"),
            "data": data
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "HR-Data-Hub-Webhook/1.0"
        }
        
        # Add signature if secret exists
        if webhook.secret:
            signature = WebhookService._generate_signature(
                json.dumps(payload), 
                webhook.secret
            )
            headers["X-Hub-Signature-256"] = f"sha256={signature}"
        
        try:
            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Webhook {webhook.id} sent successfully")
        except Exception as e:
            logger.error(f"Failed to send webhook {webhook.id}: {e}")
    
    @staticmethod
    def _generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook verification"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()