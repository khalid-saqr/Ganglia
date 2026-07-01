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


def test_trace_store_enables_wal_busy_timeout_and_listing_indexes(tmp_path):
    store = TraceStore(tmp_path / "traces.sqlite")

    with store._connect() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        index_names = {
            row[1]
            for row in conn.execute("PRAGMA index_list('traces')").fetchall()
        }

    assert journal_mode == "wal"
    assert busy_timeout == 5_000
    assert "idx_traces_timestamp" in index_names
    assert "idx_traces_operator_timestamp" in index_names
    assert "idx_traces_model_timestamp" in index_names


def test_trace_store_supports_concurrent_saves_and_lists(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    store = TraceStore(tmp_path / "traces.sqlite")

    def save_trace(index: int) -> str:
        trace = ReasoningTrace.new(
            operator="coordinate_game",
            model="test",
            user_message=f"hello {index}",
            compiled_messages=[],
        )
        store.save(trace)
        assert len(store.list_recent(10)) >= 1
        return trace.trace_id

    with ThreadPoolExecutor(max_workers=8) as executor:
        trace_ids = list(executor.map(save_trace, range(40)))

    assert len(set(trace_ids)) == 40
    assert {row["trace_id"] for row in store.list_recent(100)} == set(trace_ids)
