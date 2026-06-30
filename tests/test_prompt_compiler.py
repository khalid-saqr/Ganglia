from ganglia_runtime.operator_loader import OperatorRegistry
from ganglia_runtime.prompt_compiler import compile_messages


def test_prompt_compiler_includes_operator_rules():
    spec = OperatorRegistry().load(None).get("coordinate_game")
    messages = compile_messages(spec, "Map remote work")
    assert messages[0]["role"] == "system"
    assert "Coordinate Game" in messages[0]["content"]
    assert "Map remote work" in messages[1]["content"]
