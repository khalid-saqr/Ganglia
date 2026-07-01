from ganglia_runtime.openai_compat import messages_to_user_message, model_to_operator


def test_messages_to_user_message():
    msg = messages_to_user_message([
        {"role": "system", "content": "be careful"},
        {"role": "user", "content": "hello"},
    ])
    assert "be careful" in msg
    assert "hello" in msg


def test_messages_to_user_message_mixed_text_and_non_text_content():
    msg = messages_to_user_message([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "first"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
                {"type": "input_text", "text": "second"},
                {"type": "file", "file": {"file_id": "file_123"}},
                {"type": "tool_result", "content": "ignored tool output"},
            ],
        }
    ])

    assert msg == "[user] first\nsecond"
    assert "image" not in msg
    assert "file_123" not in msg
    assert "tool" not in msg


def test_messages_to_user_message_empty_content_arrays_return_empty_message():
    assert messages_to_user_message([{"role": "user", "content": []}]) == ""


def test_messages_to_user_message_ignores_non_string_text_values():
    msg = messages_to_user_message([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": {"value": "not accepted"}},
                {"type": "input_text", "text": 123},
                {"type": "text", "text": "usable"},
            ],
        }
    ])

    assert msg == "[user] usable"
    assert "not accepted" not in msg
    assert "123" not in msg


def test_messages_to_user_message_assistant_only_messages_are_ignored():
    assert messages_to_user_message([{"role": "assistant", "content": "hello from assistant"}]) == ""


def test_messages_to_user_message_unsupported_multimodal_inputs_return_empty_message():
    msg = messages_to_user_message([
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "https://example.test/image.png"}},
                {"type": "input_image", "image_url": "https://example.test/image.png"},
                {"type": "file", "file": {"file_id": "file_123"}},
            ],
        }
    ])

    assert msg == ""


def test_model_to_operator():
    assert model_to_operator("ganglia/grid_game") == "grid_game"
    assert model_to_operator("other") == "auto"
