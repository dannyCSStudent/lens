from fastapi import Request
import json


async def email_rate_limit_key(request: Request) -> str:
    try:
        body = await request.body()
        data = json.loads(body)

        email = data.get("email")

        if email:
            return f"email:{email.lower()}"

    except Exception:
        pass

    # fallback to IP if no email
    return request.client.host
