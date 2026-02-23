import re
from typing import Annotated
from pydantic import BaseModel, EmailStr, field_validator, StringConstraints


UsernameStr = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
    ),
]

PasswordStr = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
    ),
]

TokenStr = Annotated[
    str,
    StringConstraints(
        min_length=32,
        max_length=256,
    ),
]

class VerifyEmailSchema(BaseModel):
    token: TokenStr



class RegisterSchema(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain a number")
        return v
