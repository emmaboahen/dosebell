import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

DEFAULT_DB_URL = "sqlite:///dosebell_jobs.sqlite"
MACOS_SOUND = "/System/Library/Sounds/Ping.aiff"

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        db_url = os.environ.get("DOSELL_DB_URL", DEFAULT_DB_URL)
        _scheduler = BackgroundScheduler(
            jobstores={"default": SQLAlchemyJobStore(url=db_url)}
        )
        _scheduler.start()
        logger.info("Scheduler started (job store: %s)", db_url)
    return _scheduler


def notify(title: str, message: str) -> None:
    logger.info("%s: %s", title, message)
    if sys.platform == "darwin":
        script = (
            f"display dialog {json.dumps(message)} "
            f"with title {json.dumps(title)} "
            'buttons {"OK"} default button "OK" giving up after 60'
        )
        if os.path.exists(MACOS_SOUND):
            subprocess.Popen(
                ["afplay", MACOS_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
    elif sys.platform.startswith("linux"):
        result = subprocess.run(
            ["notify-send", title, message], capture_output=True, text=True
        )
    else:
        print(f"[{title}] {message}")
        return

    if result.returncode != 0:
        logger.warning("Popup delivery failed: %s", result.stderr.strip())


def deliver_reminder(message: str) -> None:
    notify("dosebell", message)


def schedule_reminder(
    run_at: datetime, message: str, reminder_id: str | None = None
) -> str:
    job = get_scheduler().add_job(
        deliver_reminder,
        trigger="date",
        run_date=run_at,
        args=[message],
        id=reminder_id,
        replace_existing=True,
        misfire_grace_time=3600,
    )
    return job.id


def pending_jobs():
    if _scheduler is None:
        return []
    return _scheduler.get_jobs()


def scheduled_reminders() -> list[dict]:
    reminders = []
    for job in get_scheduler().get_jobs():
        next_run = getattr(job, "next_run_time", None)
        reminders.append(
            {
                "id": job.id,
                "next_run_time": (
                    next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else None
                ),
                "message": job.args[0] if job.args else None,
            }
        )
    return reminders


def remove_reminder(reminder_id: str) -> bool:
    scheduler = get_scheduler()
    if scheduler.get_job(reminder_id) is None:
        return False
    scheduler.remove_job(reminder_id)
    return True


def wait_for_pending_reminders(poll_seconds: float = 1.0) -> None:
    while pending_jobs():
        time.sleep(poll_seconds)
