import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limit import limiter
from app.api.routes import (
    posts,
    admin_moderation,
    notifications,
    replies,
    likes,
    auth,
    admin_security
)

app = FastAPI(
    title="Lens API",
    version="0.1.0",
    description="Public discourse, evidence, and moderation API",
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Rate Limiting ----
DISABLE_RATE_LIMITS = os.getenv("DISABLE_RATE_LIMITS") == "1"

app.state.limiter = limiter

if not DISABLE_RATE_LIMITS:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# ---- Routers ----
app.include_router(posts.router)
app.include_router(replies.router)
app.include_router(admin_moderation.router)
app.include_router(notifications.router)
app.include_router(likes.router)
app.include_router(auth.router)
app.include_router(admin_security.router)

# ---- Health check ----
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
