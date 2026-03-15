from app.services.graph_intelligence import analyze_post_network


async def analyze_post(session, post_id):

    metrics = await analyze_post_network(session, post_id)

    return {
        "metrics": metrics,
        "single_source_risk": metrics["unique_sources"] <= 1,
        "confirmation_cluster": metrics["supporting_evidence"] >= 4,
    }
