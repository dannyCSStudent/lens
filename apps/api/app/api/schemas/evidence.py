from uuid import UUID
from typing import Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


EvidenceTypeLiteral = Literal["link", "document", "image", "quote"]
EvidenceDirectionLiteral = Literal["supports", "contradicts"]


class EvidenceCreate(BaseModel):
    post_id: UUID
    evidence_type: EvidenceTypeLiteral
    direction: EvidenceDirectionLiteral
    source_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Summary of what the evidence demonstrates.",
    )
    source_url: Optional[HttpUrl] = None
    upload_path: Optional[str] = None

    @field_validator("source_description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 10:
            raise ValueError("Source description must be at least 10 characters.")
        return normalized


class EvidenceResponse(BaseModel):
    id: UUID
    post_id: UUID
    evidence_type: EvidenceTypeLiteral
    direction: EvidenceDirectionLiteral
    source_description: str
    source_url: Optional[str]
    upload_path: Optional[str]

    weight: float | None = None
    source_id: Optional[UUID] = None

    created_at: Optional[datetime]

    class Config:
        from_attributes = True
