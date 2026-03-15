EVIDENCE_TYPE_MULTIPLIER = {
    "link": 1.0,
    "document": 2.0,
    "image": 0.6,
    "quote": 0.4,
}


def calculate_evidence_weight(evidence_type: str, source_reputation: float | None):
    multiplier = EVIDENCE_TYPE_MULTIPLIER.get(evidence_type, 1.0)

    if source_reputation is None:
        source_reputation = 0.5

    return round(source_reputation * multiplier, 3)
