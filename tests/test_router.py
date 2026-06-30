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
