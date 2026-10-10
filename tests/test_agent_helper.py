import agent_helper
from agent_helper import add_user_message, add_assistant_message, text_from_message


class Block:
    def __init__(self, type, text=None):
        self.type = type
        self.text = text


class FakeMessage:
    def __init__(self, content):
        self.content = content


def test_add_user_message_appends_tool_results():
    messages = []
    add_user_message(messages, [{"type": "tool_result", "tool_use_id": "t1"}])

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == [{"type": "tool_result", "tool_use_id": "t1"}]


def test_add_assistant_message_uses_message_content(monkeypatch):
    monkeypatch.setattr(agent_helper, "Message", FakeMessage)

    messages = []
    blocks = [Block("text", "hello")]
    add_assistant_message(messages, FakeMessage(blocks))

    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] is blocks


def test_text_from_message_joins_text_blocks_only():
    message = FakeMessage(
        [Block("text", "a"), Block("tool_use"), Block("text", "b")]
    )
    assert text_from_message(message) == "a\nb"


def test_text_from_message_empty_when_no_text():
    message = FakeMessage([Block("tool_use")])
    assert text_from_message(message) == ""
