def calculate_credibility_score(
    evidence_weight: float | None,
    source_reputation: float | None,
    tampered: bool,
) -> float:

    weight = evidence_weight or 0.3
    reputation = source_reputation or 0.5

    score = 0.0

    score += weight * 0.5
    score += reputation * 0.4

    if tampered:
        score -= 0.6

    return max(0.0, min(score, 1.0))
