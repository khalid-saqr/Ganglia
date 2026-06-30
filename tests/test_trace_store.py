from ganglia_runtime.trace_store import ReasoningTrace, TraceStore


def test_trace_round_trip(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    trace = ReasoningTrace.new(operator="coordinate_game", model="test", user_message="hello", compiled_messages=[])
    trace.final_answer = "answer"
    store.save(trace)
    loaded = store.get(trace.trace_id)
    assert loaded["final_answer"] == "answer"
    assert store.list_recent()[0]["trace_id"] == trace.trace_id
