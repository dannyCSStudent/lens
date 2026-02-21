from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import (
    decode_token,
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    hash_token)
from app.core.database import get_db
from app.core.models import User, RefreshToken
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])


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
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
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
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # --------------------------------------------------
    # Find user by email
    # --------------------------------------------------
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # --------------------------------------------------
    # Create Tokens
    # --------------------------------------------------
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # --------------------------------------------------
    # Store Hashed Refresh Token
    # --------------------------------------------------
    refresh_token_entry = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_token(refresh_token),
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
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # -----------------------------------------
    # Decode token
    # -----------------------------------------
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")

    # -----------------------------------------
    # Check DB for token
    # -----------------------------------------
    token_hash = hash_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Refresh token not recognized")

    # -----------------------------------------
    # Check expiration
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
    # Issue new tokens
    # -----------------------------------------
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
