from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import posts, admin_moderation, notifications, replies, likes

app = FastAPI(
    title="Lens API",
    version="0.1.0",
    description="Public discourse, evidence, and moderation API",
)

# ---- CORS (safe defaults for local dev) ----
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

# ---- Routers ----
app.include_router(posts.router)
app.include_router(replies.router)
app.include_router(admin_moderation.router)
app.include_router(notifications.router)
app.include_router(likes.router)


# ---- Health check ----
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
