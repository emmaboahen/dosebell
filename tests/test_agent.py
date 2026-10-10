import agent


class Block:
    def __init__(self, type, text=None, name=None, input=None, id=None):
        self.type = type
        self.text = text
        self.name = name
        self.input = input
        self.id = id


class FakeResponse:
    def __init__(self, content, stop_reason):
        self.content = content
        self.stop_reason = stop_reason


def test_run_conversation_loops_until_no_tool_use(monkeypatch):
    responses = [
        FakeResponse([Block("tool_use", name="get_current_datetime", id="t1")], "tool_use"),
        FakeResponse([Block("text", text="done")], "end_turn"),
    ]
    calls = {"chat": 0}

    def fake_chat(messages, system=None, tools=None):
        calls["chat"] += 1
        return responses[calls["chat"] - 1]

    monkeypatch.setattr(agent, "chat", fake_chat)
    monkeypatch.setattr(
        agent,
        "run_tools",
        lambda response: [{"type": "tool_result", "tool_use_id": "t1", "content": "{}", "is_error": False}],
    )

    messages = []
    result = agent.run_conversation(messages)

    assert result is messages
    assert calls["chat"] == 2
    assert [m["role"] for m in messages] == ["assistant", "user", "assistant"]


def test_run_conversation_returns_immediately_without_tools(monkeypatch):
    monkeypatch.setattr(
        agent,
        "chat",
        lambda messages, system=None, tools=None: FakeResponse(
            [Block("text", text="hi")], "end_turn"
        ),
    )
    run_tools_called = {"value": False}

    def fake_run_tools(response):
        run_tools_called["value"] = True
        return []

    monkeypatch.setattr(agent, "run_tools", fake_run_tools)

    messages = []
    agent.run_conversation(messages)

    assert run_tools_called["value"] is False
    assert [m["role"] for m in messages] == ["assistant"]


def test_run_conversation_forwards_system_prompt(monkeypatch):
    captured = {}

    def fake_chat(messages, system=None, tools=None):
        captured["system"] = system
        captured["tools"] = tools
        return FakeResponse([Block("text", text="hi")], "end_turn")

    monkeypatch.setattr(agent, "chat", fake_chat)
    agent.run_conversation([])

    assert captured["system"] == agent.SYSTEM_PROMPT
    assert captured["tools"] == agent.TOOLS
