from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.schemas.reply import ReplyCreate, ReplyRead
from app.services.reply_service import create_reply, get_replies_for_post
from app.api.schemas.reply import ReplyTreeRead
from app.api.deps.reply_tree import build_reply_tree
from app.core.database import get_db
from app.core.models.user import User
from app.core.models.reply import Reply
from app.core.auth.dependencies import get_current_user

router = APIRouter(prefix="/replies", tags=["replies"])

@router.post("/replies", response_model=ReplyRead)
async def create_reply(
    data: ReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate parent reply only if provided
    if data.parent_reply_id:
        parent = await db.get(Reply, data.parent_reply_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent reply not found")

    reply = Reply(
        post_id=data.post_id,
        author_id=current_user.id,
        body=data.body,
        parent_reply_id=data.parent_reply_id,  # ✅ matches model
    )

    db.add(reply)
    await db.commit()
    await db.refresh(reply)
    return reply


@router.get(
    "/posts/{post_id}/replies",
    response_model=list[ReplyTreeRead],
)
async def list_replies(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    replies = await get_replies_for_post(db, post_id)
    return build_reply_tree(replies)
