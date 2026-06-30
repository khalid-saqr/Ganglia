from pathlib import Path

from ganglia_runtime.operator_loader import OperatorRegistry, load_operator_file


def test_builtin_operators_load():
    registry = OperatorRegistry().load(None)
    assert "coordinate_game" in registry.operators
    assert "grid_game" in registry.operators
    assert "adversarial_grid_chain" in registry.operators


def test_json_operator_file_loads(tmp_path: Path):
    path = tmp_path / "simple.lg.json"
    path.write_text(
        '{"id":"simple_game","name":"Simple Game","version":"1.0.0","category":"engine","system_prompt":"x","prompt_template":"{{ user_message }}","output_schema":{"type":"object","required":["final_answer"],"properties":{"final_answer":{"type":"string"}}},"repair_prompt":"repair"}',
        encoding="utf-8",
    )
    spec = load_operator_file(path)
    assert spec.id == "simple_game"
