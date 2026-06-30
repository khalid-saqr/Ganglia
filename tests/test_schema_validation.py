from ganglia_runtime.operator_loader import OperatorRegistry
from ganglia_runtime.validators import validate_output


def test_coordinate_validates_good_output():
    spec = OperatorRegistry().load(None).get("coordinate_game")
    obj = {
        "operator": "coordinate_game",
        "ontology": ["Remote Work"],
        "x_axis": "Operational Overhead: 0 none, 10 extreme",
        "y_axis": "Knowledge Siloing: 0 none, 10 extreme",
        "placements": [
            {
                "entity": "Remote Work",
                "x_coordinate": 6.5,
                "y_coordinate": 7.0,
                "x_justification": "Coordination systems and meetings add measurable management burden.",
                "y_justification": "Informal knowledge transfer can weaken without deliberate documentation."
            }
        ],
        "assumptions": ["Knowledge-intensive organisation."],
        "failure_conditions": ["Strong documentation culture lowers siloing."],
        "final_answer": "Remote work is placed at moderately high overhead and high siloing under ordinary knowledge-work conditions."
    }
    assert validate_output(spec, obj) == []


def test_coordinate_rejects_bad_coordinate():
    spec = OperatorRegistry().load(None).get("coordinate_game")
    obj = {
        "operator": "coordinate_game",
        "ontology": ["Remote Work"],
        "x_axis": "Operational Overhead",
        "y_axis": "Knowledge Siloing",
        "placements": [
            {
                "entity": "Remote Work",
                "x_coordinate": 15,
                "y_coordinate": 7,
                "x_justification": "Coordination systems and meetings add measurable management burden.",
                "y_justification": "Informal knowledge transfer can weaken without deliberate documentation."
            }
        ],
        "assumptions": ["Assumption."],
        "failure_conditions": ["Failure."],
        "final_answer": "Remote work placement is invalid because one coordinate exceeds the bounded scale."
    }
    assert validate_output(spec, obj)
