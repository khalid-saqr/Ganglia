from ganglia_runtime.openai_compat import messages_to_user_message, model_to_operator


def test_messages_to_user_message():
    msg = messages_to_user_message([
        {"role": "system", "content": "be careful"},
        {"role": "user", "content": "hello"},
    ])
    assert "be careful" in msg
    assert "hello" in msg


def test_model_to_operator():
    assert model_to_operator("ganglia/grid_game") == "grid_game"
    assert model_to_operator("other") == "auto"
