from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.schemas.reply import ReplyCreate, ReplyRead
from app.services.reply_service import create_reply, get_replies_for_post, get_children_for_reply
from app.api.schemas.reply import ReplyTreeRead
from app.api.deps.reply_tree import build_reply_tree
from app.core.database import get_db
from app.core.models.user import User
from app.core.models.reply import Reply
from app.core.auth.dependencies import get_current_user
from typing import List, Optional
from app.core.enums import ContentStatus


router = APIRouter(prefix="/replies", tags=["replies"])

@router.post("", response_model=ReplyRead)
async def create_reply_route(
    data: ReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = await create_reply(
        db,
        post_id=data.post_id,
        author_id=current_user.id,
        body=data.body,
        parent_id=data.parent_reply_id,
    )

    return reply




@router.get("/{post_id}/replies", response_model=List[ReplyRead])
async def list_replies(
    post_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    load_children: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns top-level replies for a post.
    If load_children=True, fetch nested replies recursively.
    """
    return await get_replies_for_post(
        db, 
        post_id, 
        limit=limit, 
        offset=offset, 
        load_children=load_children
    )

@router.get("/{reply_id}/children", response_model=List[ReplyRead])
async def fetch_reply_children(
    reply_id: UUID,
    db: AsyncSession = Depends(get_db),
    status: Optional[ContentStatus] = Query(ContentStatus.active),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Fetch direct children of a single reply (lazy).
    Pagination supported.
    """
    children = await get_children_for_reply(
        db,
        parent_reply_id=reply_id,  # use the correct keyword argument
        status=status,
        limit=limit,
        offset=offset,
    )
    return children
