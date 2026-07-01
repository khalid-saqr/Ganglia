from ganglia_runtime.config import Settings
from ganglia_runtime.ollama_client import ChatResult, ChatUsage
from ganglia_runtime.runtime import GangliaRuntime
from ganglia_runtime.trace_store import TraceStore


class FakeClient:
    def chat(self, *, model, messages, schema, temperature=0.2):
        return '''{
          "operator": "coordinate_game",
          "ontology": ["Remote Work"],
          "x_axis": "Operational Overhead: 0 none, 10 extreme",
          "y_axis": "Knowledge Siloing: 0 none, 10 extreme",
          "placements": [{
            "entity": "Remote Work",
            "x_coordinate": 6.5,
            "y_coordinate": 7.0,
            "x_justification": "Remote work raises coordination overhead through meetings and tracking systems.",
            "y_justification": "Remote work can reduce informal transfer unless documentation rituals are strong."
          }],
          "assumptions": ["Knowledge work context."],
          "failure_conditions": ["A mature async documentation culture would reduce both scores."],
          "final_answer": "Remote work is mapped to moderately high operational overhead and high knowledge siloing under ordinary knowledge-work assumptions."
        }'''


def test_runtime_with_fake_client(tmp_path):
    settings = Settings(trace_db=str(tmp_path / "traces.sqlite"), operators_dir=str(tmp_path / "operators"))
    runtime = GangliaRuntime(settings=settings, llm_client=FakeClient(), trace_store=TraceStore(tmp_path / "traces.sqlite"))
    result = runtime.reason("Map remote work against operational overhead and knowledge siloing.", operator="coordinate_game")
    assert result["operator"] == "coordinate_game"
    assert "Remote work" in result["answer"]


class FakeClientWithUsage:
    def chat(self, *, model, messages, schema, temperature=0.2):
        return ChatResult(
            content='''{
              "operator": "coordinate_game",
              "ontology": ["Remote Work"],
              "x_axis": "Operational Overhead: 0 none, 10 extreme",
              "y_axis": "Knowledge Siloing: 0 none, 10 extreme",
              "placements": [{
                "entity": "Remote Work",
                "x_coordinate": 6.5,
                "y_coordinate": 7.0,
                "x_justification": "Remote work raises coordination overhead through meetings and tracking systems.",
                "y_justification": "Remote work can reduce informal transfer unless documentation rituals are strong."
              }],
              "assumptions": ["Knowledge work context."],
              "failure_conditions": ["A mature async documentation culture would reduce both scores."],
              "final_answer": "Remote work is mapped to moderately high operational overhead and high knowledge siloing under ordinary knowledge-work assumptions."
            }''',
            usage=ChatUsage(prompt_tokens=13, completion_tokens=17),
        )


def test_runtime_propagates_backend_usage(tmp_path):
    settings = Settings(trace_db=str(tmp_path / "traces.sqlite"), operators_dir=str(tmp_path / "operators"))
    runtime = GangliaRuntime(settings=settings, llm_client=FakeClientWithUsage(), trace_store=TraceStore(tmp_path / "traces.sqlite"))

    result = runtime.reason("Map remote work against operational overhead and knowledge siloing.", operator="coordinate_game")

    assert result["usage"] == {"prompt_tokens": 13, "completion_tokens": 17, "total_tokens": 30}
