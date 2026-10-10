import json

import pytest

import tools.runner as runner


class Block:
    def __init__(self, type, name=None, input=None, id=None):
        self.type = type
        self.name = name
        self.input = input
        self.id = id


class FakeMessage:
    def __init__(self, content):
        self.content = content


def test_run_tools_returns_result_blocks(monkeypatch):
    monkeypatch.setattr(runner, "get_current_datetime", lambda **kwargs: "NOW")

    message = FakeMessage([Block("tool_use", "get_current_datetime", {}, "t1")])
    blocks = runner.run_tools(message)

    assert len(blocks) == 1
    assert blocks[0]["type"] == "tool_result"
    assert blocks[0]["tool_use_id"] == "t1"
    assert blocks[0]["is_error"] is False
    assert json.loads(blocks[0]["content"]) == "NOW"


def test_run_tools_captures_errors(monkeypatch):
    def boom(**kwargs):
        raise ValueError("nope")

    monkeypatch.setattr(runner, "get_current_datetime", boom)

    message = FakeMessage([Block("tool_use", "get_current_datetime", {}, "t1")])
    blocks = runner.run_tools(message)

    assert blocks[0]["is_error"] is True
    assert "nope" in json.loads(blocks[0]["content"])["error"]


def test_run_tool_dispatches_by_name(monkeypatch):
    monkeypatch.setattr(runner, "set_reminder", lambda **kwargs: "ok")
    assert runner.run_tool("set_reminder", {"reminder_time_str": "x"}) == "ok"


def test_run_tool_dispatches_list_reminders(monkeypatch):
    monkeypatch.setattr(runner, "list_reminders", lambda: "listed")
    assert runner.run_tool("list_reminders", {}) == "listed"


def test_run_tool_dispatches_cancel_reminder(monkeypatch):
    monkeypatch.setattr(runner, "cancel_reminder", lambda **kwargs: kwargs["reminder_id"])
    assert runner.run_tool("cancel_reminder", {"reminder_id": "abc"}) == "abc"


def test_run_tool_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unknown tool"):
        runner.run_tool("nope", {})
