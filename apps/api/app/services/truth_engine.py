from sqlalchemy import text


async def calculate_truth_score(session, post_id: str):
    result = await session.execute(
        text("""
        SELECT
            SUM(CASE WHEN direction='support' THEN weight ELSE 0 END) AS support,
            SUM(CASE WHEN direction='contradict' THEN weight ELSE 0 END) AS contradict
        FROM evidence
        WHERE post_id = :post_id
        """),
        {"post_id": post_id},
    )

    row = result.first()

    support = row.support or 0
    contradict = row.contradict or 0

    total = support + contradict

    if total == 0:
        return 0.5, "low"

    score = support / total

    if score > 0.8:
        confidence = "high"
    elif score > 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    return score, confidence
