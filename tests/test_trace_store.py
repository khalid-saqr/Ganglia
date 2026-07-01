from ganglia_runtime.trace_store import ReasoningTrace, TraceStore


def test_trace_round_trip(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    trace = ReasoningTrace.new(operator="coordinate_game", model="test", user_message="hello", compiled_messages=[])
    trace.final_answer = "answer"
    store.save(trace)
    loaded = store.get(trace.trace_id)
    assert loaded["final_answer"] == "answer"
    assert store.list_recent()[0]["trace_id"] == trace.trace_id


def test_list_recent_clamps_limit_to_supported_bounds(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")
    for index in range(3):
        trace = ReasoningTrace.new(
            operator="coordinate_game",
            model="test",
            user_message=f"hello {index}",
            compiled_messages=[],
        )
        store.save(trace)

    assert len(store.list_recent(0)) == 1
    assert len(store.list_recent(-10)) == 1
    assert len(store.list_recent(10_000)) == 3
