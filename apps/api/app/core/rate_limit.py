from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
import os


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
# Global limiter using Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL
)


def email_rate_limit_key(request: Request) -> str:
    try:
        body = request._body  # FastAPI already stores body here
        if body:
            data = json.loads(body)
            email = data.get("email")

            if email:
                return f"email:{email.lower()}"

    except Exception:
        pass

    # fallback to IP
    return request.client.host