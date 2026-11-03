import hmac
from fastapi import Header, Query, HTTPException
from app.config import WEBHOOK_SECRET


def verify_token(
    x_webhook_secret: str | None = Header(None, alias="X-Webhook-Secret"),
    token: str | None = Query(None),
):
    provided = x_webhook_secret or token
    if not provided or not hmac.compare_digest(provided, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid or missing secret token")
