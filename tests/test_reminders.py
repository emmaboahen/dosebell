import logging
import types
from datetime import datetime, timedelta

import pytest
from apscheduler.schedulers.background import BackgroundScheduler

import reminders


@pytest.fixture
def memory_scheduler(monkeypatch):
    scheduler = BackgroundScheduler()
    scheduler.start()
    monkeypatch.setattr(reminders, "_scheduler", scheduler)
    yield scheduler
    scheduler.shutdown(wait=False)


def test_schedule_reminder_adds_pending_job(memory_scheduler):
    job_id = reminders.schedule_reminder(
        datetime.now() + timedelta(hours=1), "take meds"
    )
    assert job_id in [job.id for job in reminders.pending_jobs()]


def test_pending_jobs_empty_without_scheduler(monkeypatch):
    monkeypatch.setattr(reminders, "_scheduler", None)
    assert reminders.pending_jobs() == []


def test_scheduled_reminders_reports_message_and_id(memory_scheduler):
    job_id = reminders.schedule_reminder(
        datetime.now() + timedelta(hours=1), "take meds"
    )
    listed = reminders.scheduled_reminders()
    assert [r["id"] for r in listed] == [job_id]
    assert listed[0]["message"] == "take meds"
    assert listed[0]["next_run_time"] is not None


def test_remove_reminder_deletes_job(memory_scheduler):
    job_id = reminders.schedule_reminder(
        datetime.now() + timedelta(hours=1), "take meds"
    )
    assert reminders.remove_reminder(job_id) is True
    assert reminders.scheduled_reminders() == []


def test_remove_reminder_returns_false_for_unknown(memory_scheduler):
    assert reminders.remove_reminder("ghost") is False


def test_wait_for_pending_reminders_returns_when_idle(monkeypatch):
    monkeypatch.setattr(reminders, "_scheduler", None)
    reminders.wait_for_pending_reminders(poll_seconds=0)


def test_deliver_reminder_calls_notify(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        reminders, "notify", lambda title, message: captured.update(message=message)
    )
    reminders.deliver_reminder("take meds")
    assert captured["message"] == "take meds"


def test_notify_darwin_uses_dialog(monkeypatch):
    captured = {}

    class Result:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return Result()

    monkeypatch.setattr(reminders, "sys", types.SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(reminders.os.path, "exists", lambda path: False)
    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    reminders.notify("dosebell", "take meds")

    script = captured["cmd"][-1]
    assert "display dialog" in script
    assert "take meds" in script


def test_notify_linux_uses_notify_send(monkeypatch):
    captured = {}

    class Result:
        returncode = 0
        stderr = ""

    monkeypatch.setattr(reminders, "sys", types.SimpleNamespace(platform="linux"))
    monkeypatch.setattr(
        reminders.subprocess,
        "run",
        lambda cmd, **kwargs: (captured.update(cmd=cmd), Result())[1],
    )

    reminders.notify("dosebell", "take meds")

    assert captured["cmd"] == ["notify-send", "dosebell", "take meds"]


def test_notify_other_platform_prints(monkeypatch, capsys):
    monkeypatch.setattr(reminders, "sys", types.SimpleNamespace(platform="win32"))
    reminders.notify("dosebell", "take meds")
    assert "[dosebell] take meds" in capsys.readouterr().out


def test_notify_logs_warning_on_failure(monkeypatch, caplog):
    class Result:
        returncode = 1
        stderr = "boom"

    monkeypatch.setattr(reminders, "sys", types.SimpleNamespace(platform="linux"))
    monkeypatch.setattr(reminders.subprocess, "run", lambda cmd, **kwargs: Result())

    with caplog.at_level(logging.WARNING):
        reminders.notify("dosebell", "take meds")

    assert "boom" in caplog.text
