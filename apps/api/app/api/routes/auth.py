from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
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
from app.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    mark_successful_login,
)
from app.core.auth.dependencies import get_current_user
from app.api.schemas.password_reset import PasswordResetRequest, PasswordResetConfirm   
from app.api.schemas.auth import VerifyEmailSchema, RegisterSchema, ResendVerificationSchema
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.utils.security import log_security_event
from app.core.enums import SecurityEventType
from app.core.utils.generate_token import generate_verification_token
from app.core.utils.network import get_real_ip
from app.core.rate_limit import email_rate_limit_key
from app.core.rate_limit import limiter
from app.core.securities.login_detection import detect_suspicious_login
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.cache.redis import (
    add_revoked_session,
    is_session_revoked,
    redis_client,
)



router = APIRouter(prefix="/auth", tags=["auth"])

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
RESET_TOKEN_EXPIRY_MINUTES = 15
IDLE_TIMEOUT_MINUTES = 30

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


@router.post("/register")
@limiter.limit("20/minute")
@limiter.limit("5/minute", key_func=email_rate_limit_key)
async def register(
    request: Request,
    payload: RegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_username = await get_user_by_username(db, payload.username)
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken",
        )

    # Create user
    user = await create_user(
        db,
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )

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

from fastapi import Response, Cookie

@router.post("/login")
@limiter.limit("10/minute", key_func=email_rate_limit_key)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):

    user = await get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    # Account lock check
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

    # Password verification
    if not verify_password(data.password, user.password_hash):

        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        await log_security_event(
            db,
            SecurityEventType.login_failed,
            request,
            user_id=str(user.id),
        )

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_login_attempts = 0

            await log_security_event(
                db,
                SecurityEventType.account_locked,
                request,
                user_id=str(user.id),
            )

        await db.commit()

        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    ip_address = request.headers.get(
        "x-forwarded-for",
        request.client.host
    )

    await detect_suspicious_login(
        db,
        request,
        user,
        ip_address = get_real_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


    # ✅ SUCCESS
    await mark_successful_login(db, user)

    # 🔥 1️⃣ Generate session UUID FIRST
    refresh_session_id = uuid.uuid4()

    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        .order_by(RefreshToken.created_at.asc())
    )

    active_sessions = result.scalars().all()

    MAX_SESSIONS = 5

    if len(active_sessions) >= MAX_SESSIONS:
        oldest_session = active_sessions[0]
        oldest_session.is_revoked = True


    # 🔥 2️⃣ Create refresh JWT bound to session ID
    refresh_token_value = create_refresh_token(
        str(user.id),
        session_id=str(refresh_session_id),
    )

    # 🔥 3️⃣ Create DB entry using same ID
    refresh_token_entry = RefreshToken(
        id=refresh_session_id,
        user_id=user.id,
        token_hash=hash_token(refresh_token_value),
        device_name=None,
        ip_address = get_real_ip(request),
        user_agent=request.headers.get("user-agent"),
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False,
    )

    print("Refresh token value:", refresh_token_value)

    db.add(refresh_token_entry)

    # 🔐 4️⃣ Create access token linked to same session
    access_token = create_access_token(
        str(user.id),
        session_id=str(refresh_session_id),
    )

    await log_security_event(
        db,
        SecurityEventType.login_success,
        request,
        user_id=str(user.id),
    )

    await db.commit()

    # 🔐 5️⃣ Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=60 * 15,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token_value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return {"message": "Login successful"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            token_sid = payload.get("sid")
        except JWTError:
            token_sid = None

        token_hash = hash_token(refresh_token)

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.is_revoked = True

        # 🔴 Instant Redis revoke
        if token_sid:
            await redis_client.set(
                f"revoked:{token_sid}",
                "1",
                ex=60 * 60 * 24 * 7
            )


    await log_security_event(
        db,
        SecurityEventType.logout,
        request,
    )

    await db.commit()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out"}


@router.post("/password-reset/request")
@limiter.limit("3/minute")
@limiter.limit("5/hour", key_func=email_rate_limit_key)
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
    user.failed_login_attempts = 0
    user.locked_until = None

    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,
        )
        .values(is_revoked=True)
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
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    access_token = request.cookies.get("access_token")
    current_session_id = None

    if access_token:
        payload = decode_token(access_token)
        if payload:
            current_session_id = payload.get("sid")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )

    sessions = result.scalars().all()

    return {
        "current_session_id": current_session_id,
        "sessions": [
            {
                "id": str(s.id),
                "device_name": s.device_name,
                "ip_address": s.ip_address,
                "created_at": s.created_at,
                "last_used_at": s.last_used_at,
                "expires_at": s.expires_at,
            }
            for s in sessions
        ],
    }


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

    session.is_revoked = True

    # 🚀 instant revocation
    await redis_client.set(f"revoked:{session_id}", "1")

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


@router.post("/resend-verification")
@limiter.limit("5/minute", key_func=email_rate_limit_key)
async def resend_verification(
    request: Request,
    payload: ResendVerificationSchema,
    db: AsyncSession = Depends(get_db),
):
    # Always return generic response
    generic_response = {
        "message": "If an account exists, a verification email has been sent."
    }

    # Find user
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()

    # If user doesn't exist OR already verified → return generic
    if not user or user.is_verified:
        return generic_response

    # Delete existing verification tokens
    await db.execute(
        delete(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user.id
        )
    )

    # Generate new token
    raw_token, token_hash = generate_verification_token()

    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(verification)

    # Optional: log security event
    await log_security_event(
        db,
        SecurityEventType.resend_verification,
        request,
        user_id=str(user.id),
    )

    await db.commit()

    # TODO: send email here
    verification_link = f"http://localhost:3000/verify-email?token={raw_token}"
    print("Resend verification link:", verification_link)

    return generic_response


@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    print("Incoming refresh token:", refresh_token)


    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 🔐 Decode refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_sid = payload.get("sid")

        if not user_id or not token_sid:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # 🚨 Check Redis instant revocation
        if await redis_client.get(f"revoked:{token_sid}"):
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            raise HTTPException(
                status_code=401,
                detail="Session revoked"
            )


    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )
    stored_token = result.scalar_one_or_none()

    # 🚨 REPLAY DETECTION
    if not stored_token:
        # Add user-wide revocation marker
        await redis_client.set(
            f"user_revoked:{user_id}",
            "1",
            ex=60 * 60 * 24 * 7
        )

        await log_security_event(
            db,
            SecurityEventType.refresh_token_reuse,
            request,
            user_id=str(user_id),
        )

        # Global revoke on replay
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await db.commit()

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        raise HTTPException(
            status_code=401,
            detail="Session revoked due to suspicious activity"
        )
    
    # 🔐 CRITICAL CHECK
    if str(stored_token.id) != token_sid:
        raise HTTPException(status_code=401, detail="Invalid token session")

    # 🚨 If token already revoked → replay
    if stored_token.is_revoked:
        await redis_client.set(
            f"revoked:{token_sid}",
            "1",
            ex=60 * 60 * 24 * 7
        )

        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await db.commit()

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        raise HTTPException(
            status_code=401,
            detail="Replay detected. All sessions revoked."
        )
    
    # ⏳ IDLE TIMEOUT CHECK
    if stored_token.last_used_at:
        idle_cutoff = stored_token.last_used_at + timedelta(
            minutes=IDLE_TIMEOUT_MINUTES
        )

        if idle_cutoff < datetime.now(timezone.utc):
            await redis_client.set(
                f"revoked:{token_sid}",
                "1",
                ex=60 * 60 * 24 * 7
            )

            stored_token.is_revoked = True
            await db.commit()

            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            raise HTTPException(
                status_code=401,
                detail="Session expired due to inactivity"
            )


    # Expiration check
    if stored_token.expires_at < datetime.now(timezone.utc):
        await redis_client.set(
            f"revoked:{token_sid}",
            "1",
            ex=60 * 60 * 24 * 7
        )

        stored_token.is_revoked = True
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = await db.get(User, stored_token.user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 🔄 ROTATION STARTS HERE

    stored_token.last_used_at = datetime.now(timezone.utc)


    # 1️⃣ Revoke old token
    stored_token.is_revoked = True

    await redis_client.set(
        f"revoked:{token_sid}",
        "1",
        ex=60 * 60 * 24 * 7
    )


    # 2️⃣ Create new session ID FIRST
    new_session_id = uuid.uuid4()

    # 3️⃣ Create new refresh token using that ID
    new_refresh_token_value = create_refresh_token(
        str(user.id),
        session_id=str(new_session_id),
    )

    # 4️⃣ Create DB entry using same ID
    new_refresh_entry = RefreshToken(
        id=new_session_id,
        user_id=user.id,
        token_hash=hash_token(new_refresh_token_value),
        device_name=stored_token.device_name,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False,
    )

    db.add(new_refresh_entry)
    await db.flush()

    # 5️⃣ Link chain
    stored_token.replaced_by = new_refresh_entry.id

    # 6️⃣ Issue new access token linked to new session
    new_access_token = create_access_token(
        str(user.id),
        session_id=str(new_refresh_entry.id),
    )


    await db.commit()

    # 🔐 Set cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 15,
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token_value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return {"message": "Token rotated"}


@router.delete("/sessions/revoke-others")
async def revoke_other_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(request.cookies.get("access_token"))
    current_session_id = payload.get("sid")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.id != current_session_id,
            RefreshToken.is_revoked == False,
        )
    )

    sessions = result.scalars().all()

    for s in sessions:
        s.is_revoked = True

        # 🚀 instant revoke
        await redis_client.set(f"revoked:{s.id}", "1")

    await db.commit()

    return {"message": "Other sessions revoked"}
