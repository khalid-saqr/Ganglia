from ganglia_runtime.operator_loader import OperatorRegistry
from ganglia_runtime.router import route_operator


def test_router_selects_adversarial_chain():
    registry = OperatorRegistry().load(None)
    op = route_operator("Stress-test this SaaS pricing model for failure modes", registry)
    assert op == "adversarial_grid_chain"


def test_explicit_operator_wins():
    registry = OperatorRegistry().load(None)
    op = route_operator("Stress-test this", registry, "coordinate_game")
    assert op == "coordinate_game"


def test_explicit_missing_operator_returns_normalized_id_for_runtime_error():
    registry = OperatorRegistry().load(None)
    op = route_operator("Stress-test this SaaS pricing model for failure modes", registry, "does_not_exist")
    assert op == "does_not_exist"


def test_explicit_missing_ganglia_operator_returns_normalized_id_for_runtime_error():
    registry = OperatorRegistry().load(None)
    op = route_operator("Stress-test this SaaS pricing model for failure modes", registry, "ganglia/does_not_exist")
    assert op == "does_not_exist"
