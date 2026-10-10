from datetime import datetime, timedelta

import pytest

import tools.handlers as handlers


def test_get_current_datetime_default_format():
    value = handlers.get_current_datetime()
    datetime.strptime(value, handlers.DATE_FORMAT)


def test_get_current_datetime_custom_format():
    assert len(handlers.get_current_datetime("%Y")) == 4


def test_get_current_datetime_rejects_empty_format():
    with pytest.raises(ValueError):
        handlers.get_current_datetime("")


def test_add_duration_to_datetime():
    result = handlers.add_duration_to_datetime("2026-01-01 00:00:00", 10)
    assert result == "2026-01-01 00:00:10"


def test_add_duration_rejects_empty_base():
    with pytest.raises(ValueError):
        handlers.add_duration_to_datetime("", 10)


def test_set_reminder_schedules_future_time(monkeypatch):
    captured = {}

    def fake_schedule(run_at, message, reminder_id=None):
        captured["run_at"] = run_at
        captured["message"] = message
        return "job-123"

    monkeypatch.setattr(handlers, "schedule_reminder", fake_schedule)

    future = datetime.now() + timedelta(seconds=30)
    out = handlers.set_reminder(future.strftime(handlers.DATE_FORMAT), "take meds")

    assert "job-123" in out
    assert captured["message"] == "take meds"
    assert captured["run_at"] == future.replace(microsecond=0)


def test_set_reminder_rejects_past_time(monkeypatch):
    monkeypatch.setattr(handlers, "schedule_reminder", lambda *a, **k: "job")

    past = datetime.now() - timedelta(seconds=30)
    with pytest.raises(ValueError, match="future"):
        handlers.set_reminder(past.strftime(handlers.DATE_FORMAT), "take meds")


def test_set_reminder_rejects_empty_message():
    with pytest.raises(ValueError):
        handlers.set_reminder("2099-01-01 00:00:00", "")


def test_list_reminders_reports_empty(monkeypatch):
    monkeypatch.setattr(handlers, "scheduled_reminders", lambda: [])
    assert handlers.list_reminders() == "No reminders are scheduled."


def test_list_reminders_formats_entries(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "scheduled_reminders",
        lambda: [
            {"id": "abc", "next_run_time": "2026-01-01 08:00:00", "message": "BP meds"}
        ],
    )
    out = handlers.list_reminders()
    assert "abc" in out
    assert "BP meds" in out
    assert "2026-01-01 08:00:00" in out


def test_cancel_reminder_success(monkeypatch):
    monkeypatch.setattr(handlers, "remove_reminder", lambda reminder_id: True)
    assert handlers.cancel_reminder("abc") == "Cancelled reminder abc."


def test_cancel_reminder_rejects_empty_id(monkeypatch):
    monkeypatch.setattr(handlers, "remove_reminder", lambda reminder_id: True)
    with pytest.raises(ValueError):
        handlers.cancel_reminder("")


def test_cancel_reminder_rejects_unknown_id(monkeypatch):
    monkeypatch.setattr(handlers, "remove_reminder", lambda reminder_id: False)
    with pytest.raises(ValueError, match="No reminder found"):
        handlers.cancel_reminder("ghost")
