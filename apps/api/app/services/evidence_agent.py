
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.post import Post
from app.services.archive_service import fetch_page_content
from app.services.archive_service import generate_content_hash


async def search_sources(query: str):

    # placeholder search example
    url = f"https://duckduckgo.com/?q={query}"

    return [url]


async def investigate_claim(session: AsyncSession, post_id):

    post = await session.get(Post, post_id)

    if not post:
        return

    query = post.title if hasattr(post, "title") else post.content

    urls = await search_sources(query)

    findings = []

    for url in urls:

        try:

            content = await fetch_page_content(url)

            hash_value = generate_content_hash(content)

            findings.append(
                {
                    "url": url,
                    "hash": hash_value,
                }
            )

        except Exception:
            continue

    return findings
