"""
Checks the secret token before allowing access to the webhook.
"""
from fastapi import Header, Query, HTTPException
from app.config import WEBHOOK_SECRET

def verify_token(
    x_webhook_secret: str = Header(None, alias="X-Webhook-Secret"),
    token: str = Query(None)
):
    # Accept the token from either the header or the URL query (?token=...)
    provided_token = x_webhook_secret or token
    
    if provided_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid or missing secret token")