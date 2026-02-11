from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict


class NotificationRead(BaseModel):
    id: UUID
    type: str
    payload: Dict
    read_at: Optional[datetime]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
