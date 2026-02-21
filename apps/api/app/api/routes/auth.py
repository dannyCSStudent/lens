from urllib import request
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import delete

from app.core.security import (
    decode_token,
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    hash_token,
    generate_reset_token,
)
from app.core.database import get_db
from app.core.models import User, RefreshToken
from app.core.auth.dependencies import get_current_user
from app.api.schemas.password_reset import PasswordResetRequest, PasswordResetConfirm   
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/auth", tags=["auth"])

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
RESET_TOKEN_EXPIRY_MINUTES = 15

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register")
@limiter.limit("5/minute")  # 5 attempts per IP per minute
async def register(request: Request,data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_username = await db.execute(
        select(User).where(User.username == data.username)
    )

    existing_email = await db.execute(
        select(User).where(User.email == data.email)
    )

    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username taken")

    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    
    user = User(
    email=data.email,
    username=data.username,
    password_hash=hash_password(data.password),
)


    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User created"}


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # --------------------------------------------------
    # Find user by email
    # --------------------------------------------------
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    # --------------------------------------------------
    # Prevent user enumeration
    # --------------------------------------------------
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # --------------------------------------------------
    # Check if account is locked
    # --------------------------------------------------
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=403,
            detail="Account locked. Try again later."
        )

    # --------------------------------------------------
    # Verify password
    # --------------------------------------------------
    if not verify_password(data.password, user.password_hash):

        user.failed_attempts = (user.failed_attempts or 0) + 1

        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_attempts = 0  # reset after locking

        await db.commit()

        raise HTTPException(status_code=401, detail="Invalid credentials")

    # --------------------------------------------------
    # Optional: Enforce email verification
    # --------------------------------------------------
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified."
        )

    # --------------------------------------------------
    # Successful login → reset lock fields
    # --------------------------------------------------
    user.failed_attempts = 0
    user.locked_until = None

    # --------------------------------------------------
    # Create Tokens
    # --------------------------------------------------
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))


    device_name = data.device_name if hasattr(data, "device_name") else None
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")

    # --------------------------------------------------
    # Store Hashed Refresh Token
    # --------------------------------------------------
    refresh_token_entry = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(refresh_token_entry)
    await db.commit()

    # --------------------------------------------------
    # Return Tokens
    # --------------------------------------------------
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    # -----------------------------------------
    # Decode + Validate JWT Structure First
    # -----------------------------------------
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # -----------------------------------------
    # Hash Token For DB Lookup
    # -----------------------------------------
    token_hash = hash_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()

    # -----------------------------------------
    # 🚨 REUSE DETECTION (Replay Attack Protection)
    # -----------------------------------------
    if not stored_token:
        # If token is valid JWT but not in DB,
        # it was likely already rotated → possible theft.
        # Kill all sessions for this user.

        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token reuse detected. All sessions invalidated."
        )

    # Extra safety: ensure token belongs to correct user
    if str(stored_token.user_id) != str(user_id):
        raise HTTPException(status_code=401, detail="Token mismatch")

    # -----------------------------------------
    # Check Expiration
    # -----------------------------------------
    if stored_token.expires_at < datetime.now(timezone.utc):
        await db.delete(stored_token)
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # -----------------------------------------
    # ROTATION: Delete old token
    # -----------------------------------------
    await db.delete(stored_token)

    # -----------------------------------------
    # Issue New Tokens
    # -----------------------------------------
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    stored_token.last_used_at = datetime.now(timezone.utc)


    new_refresh_entry = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=hash_token(new_refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(new_refresh_entry)
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "stored_token_last_used": stored_token.last_used_at.isoformat(),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()

    if stored_token:
        await db.delete(stored_token)
        await db.commit()

    return {"message": "Logged out"}



@router.post("/password-reset/request")
@limiter.limit("3/minute")  # prevent email spam abuse
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    # Always respond the same (no enumeration)
    if not user:
        return {"message": "If that email exists, a reset link has been sent."}

    # Generate token
    raw_token = generate_reset_token()
    hashed = hash_token(raw_token)

    user.password_reset_token_hash = hashed
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRY_MINUTES
    )

    await db.commit()

    # TODO: Send email with raw_token
    # Example reset link:
    # https://yourdomain.com/reset-password?token=<raw_token>

    print("Password reset token:", raw_token)  # remove in prod

    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
@limiter.limit("5/minute")
async def confirm_password_reset(
    request: Request,
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    hashed = hash_token(data.token)

    result = await db.execute(
        select(User).where(User.password_reset_token_hash == hashed)
    )
    user = result.scalar_one_or_none()

    if (
        not user
        or not user.password_reset_expires
        or user.password_reset_expires < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # --------------------------------------------------
    # Update password
    # --------------------------------------------------
    user.password_hash = hash_password(data.new_password)

    # Clear reset fields (single use)
    user.password_reset_token_hash = None
    user.password_reset_expires = None

    # Reset lock fields
    user.failed_attempts = 0
    user.locked_until = None

    # --------------------------------------------------
    # 🔥 Invalidate ALL refresh tokens
    # --------------------------------------------------
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user.id)
    )

    await db.commit()

    return {"message": "Password successfully reset. All sessions have been logged out."}


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id
        )
    )

    sessions = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "device_name": s.device_name,
            "ip_address": s.ip_address,
            "created_at": s.created_at,
            "last_used_at": s.last_used_at,
            "expires_at": s.expires_at,
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == current_user.id,
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    return {"message": "Session revoked"}
