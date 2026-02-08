# app/api/routes/admin_moderation.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.admin import require_admin
from app.api.schemas.moderation import ModerateRequest
from app.services.moderation_service import moderate_content
from app.core.database import get_db

router = APIRouter(
    prefix="/admin/moderation",
    tags=["admin"],
)


@router.post("")
async def moderate(
    data: ModerateRequest,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    result = await moderate_content(
        db,
        moderator_id=admin.id,
        target_type=data.target_type,
        target_id=data.target_id,
        new_status=data.new_status,
        reason=data.reason,
    )

    return {
        "success": True,
        "target_type": data.target_type,
        "target_id": data.target_id,
        "new_status": data.new_status,
    }
