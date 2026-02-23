from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import delete
import hashlib
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
from app.core.models import User, RefreshToken, EmailVerificationToken
from app.core.auth.dependencies import get_current_user
from app.api.schemas.password_reset import PasswordResetRequest, PasswordResetConfirm   
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.utils.security import log_security_event
from app.core.enums import SecurityEventType
from app.api.schemas.auth import VerifyEmailSchema, RegisterSchema
from app.core.utils.generate_token import generate_verification_token
from app.core.rate_limit import email_rate_limit_key





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
@limiter.limit("20/minute")
@limiter.limit("5/minute", key_func=email_rate_limit_key)
async def register(
    request: Request,
    payload: RegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    # Check existing email
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_verified=False,
    )

    db.add(user)
    await db.flush()  # Get user.id without committing

    # Generate verification token
    raw_token, token_hash = generate_verification_token()

    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(verification)

    await db.commit()

    # TODO: send email with raw_token
    verification_link = f"http://localhost:3000/verify-email?token={raw_token}"
    print("Verification link:", verification_link)

    return {"message": "Verification email sent"}

@router.post("/login")
@limiter.limit("5/minute", key_func=email_rate_limit_key)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    
    # Check lock
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):

        await log_security_event(
            db,
            SecurityEventType.account_locked,
            request,
            user_id=str(user.id),
        )
        await db.commit()

        raise HTTPException(
            status_code=403,
            detail="Account locked. Try again later."
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):

        user.failed_attempts = (user.failed_attempts or 0) + 1

        await log_security_event(
            db,
            SecurityEventType.login_failed,
            request,
            user_id=str(user.id),
        )

        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_attempts = 0

            await log_security_event(
                db,
                SecurityEventType.account_locked,
                request,
                user_id=str(user.id),
            )

        await db.commit()

        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Success
    user.failed_attempts = 0
    user.locked_until = None

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    refresh_token_entry = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        device_name=None,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(refresh_token_entry)

    await log_security_event(
        db,
        SecurityEventType.login_success,
        request,
        user_id=str(user.id),
    )

    await db.commit()

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

    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")

    token_hash = hash_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()

    # 🚨 REUSE DETECTION
    if not stored_token:

        await log_security_event(
            db,
            SecurityEventType.refresh_reuse_detected,
            request,
            user_id=str(user_id),
        )

        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )

        await db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token reuse detected. All sessions invalidated."
        )

    if stored_token.expires_at < datetime.now(timezone.utc):
        await db.delete(stored_token)
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    await db.delete(stored_token)

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

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
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):

    token_hash = hash_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()

    if stored_token:
        await db.delete(stored_token)

    await log_security_event(
        db,
        SecurityEventType.logout,
        request,
    )

    await db.commit()

    return {"message": "Logged out"}



@router.post("/password-reset/request")
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If that email exists, a reset link has been sent."}

    raw_token = generate_reset_token()
    hashed = hash_token(raw_token)

    user.password_reset_token_hash = hashed
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRY_MINUTES
    )

    await log_security_event(
        db,
        SecurityEventType.password_reset_requested,
        request,
        user_id=str(user.id),
    )

    await db.commit()

    print("Password reset token:", raw_token)

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

    user.password_hash = hash_password(data.new_password)
    user.password_reset_token_hash = None
    user.password_reset_expires = None
    user.failed_attempts = 0
    user.locked_until = None

    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user.id)
    )

    await log_security_event(
        db,
        SecurityEventType.password_reset_completed,
        request,
        user_id=str(user.id),
    )

    await db.commit()

    return {
        "message": "Password successfully reset. All sessions have been logged out."
    }


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


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailSchema,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hashlib.sha256(
        payload.token.encode()
    ).hexdigest()

    # Find verification record
    result = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid token")

    if record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")


    # Get user
    result = await db.execute(
        select(User).where(User.id == record.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Mark verified
    user.is_verified = True

    # Delete token record
    await db.delete(record)

    await db.commit()

    return {"message": "Email verified successfully"}
