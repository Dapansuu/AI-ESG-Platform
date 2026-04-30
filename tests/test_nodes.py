from app.graph.nodes.gap_analyzer import GapAnalyzer


def test_gap():

    node = GapAnalyzer({
        "gap_thresholds": {"red": -20, "amber": -5}
    })

    state = {
        "company_data": {"emissions": 70},
        "peer_data": {"emissions": 100}
    }

    result = node.run(state)

    assert result["kpis"][0]["status"] == "red"