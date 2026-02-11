import re
from typing import Set
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.models.user import User

MENTION_REGEX = re.compile(r"@([a-zA-Z0-9_]{3,30})")


async def extract_mentioned_user_ids(
    db: AsyncSession,
    text: str,
) -> Set[UUID]:
    usernames = set(MENTION_REGEX.findall(text))
    if not usernames:
        return set()

    result = await db.execute(
        select(User.id).where(User.username.in_(usernames))
    )

    return {row[0] for row in result.all()}
