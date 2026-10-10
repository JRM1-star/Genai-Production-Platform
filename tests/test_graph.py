from app.graph.workflow import evaluate_node, route_after_evaluation


def test_insufficient_evidence():
    state = {"evidence": []}
    result = evaluate_node(state)
    assert result["grounded"] is False
    assert route_after_evaluation({**state, **result}) == "insufficient"

def test_sufficient_evidence():
    state = {"evidence": [{"score": 0.8}]}
    result = evaluate_node(state)
    assert result["grounded"] is True
    assert route_after_evaluation({**state, **result}) == "generate"
