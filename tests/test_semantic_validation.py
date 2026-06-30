from ganglia_runtime.operator_loader import OperatorRegistry
from ganglia_runtime.validators import validate_output


def test_grid_requires_markdown_table():
    spec = OperatorRegistry().load(None).get("grid_game")
    obj = {
        "operator": "grid_game",
        "row_ontology": ["A"],
        "column_ontology": ["Cost", "Risk"],
        "rows": [{"row_label": "A", "cells": {"Cost": "Low", "Risk": "High"}, "row_assumption": "This row is illustrative."}],
        "assumptions": ["Assumption."],
        "failure_conditions": ["Failure."],
        "final_answer": "This answer has no markdown table even though the Grid Game requires one."
    }
    errors = validate_output(spec, obj)
    assert any("markdown table" in err for err in errors)
