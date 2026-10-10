from datetime import datetime, timedelta

from reminders import remove_reminder, schedule_reminder, scheduled_reminders

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_current_datetime(date_format: str = DATE_FORMAT) -> str:
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


def add_duration_to_datetime(
    base_datetime_str: str,
    duration_seconds: float,
    date_format: str = DATE_FORMAT,
) -> str:
    if not base_datetime_str:
        raise ValueError("base_datetime_str cannot be empty")
    if not date_format:
        raise ValueError("date_format cannot be empty")

    base_datetime = datetime.strptime(base_datetime_str, date_format)
    new_datetime = base_datetime + timedelta(seconds=duration_seconds)
    return new_datetime.strftime(date_format)


def set_reminder(
    reminder_time_str: str,
    reminder_message: str,
    date_format: str = DATE_FORMAT,
) -> str:
    if not reminder_time_str:
        raise ValueError("reminder_time_str cannot be empty")
    if not reminder_message:
        raise ValueError("reminder_message cannot be empty")
    if not date_format:
        raise ValueError("date_format cannot be empty")

    reminder_time = datetime.strptime(reminder_time_str, date_format)
    if reminder_time <= datetime.now():
        raise ValueError("reminder time must be in the future")

    job_id = schedule_reminder(reminder_time, reminder_message)
    return (
        f"Reminder set for {reminder_time.strftime(date_format)}: "
        f"{reminder_message} (job id: {job_id})"
    )


def list_reminders() -> str:
    reminders = scheduled_reminders()
    if not reminders:
        return "No reminders are scheduled."
    lines = [
        f"- {r['id']}: {r['message']} at {r['next_run_time']}" for r in reminders
    ]
    return "Scheduled reminders:\n" + "\n".join(lines)


def cancel_reminder(reminder_id: str) -> str:
    if not reminder_id:
        raise ValueError("reminder_id cannot be empty")
    if not remove_reminder(reminder_id):
        raise ValueError(f"No reminder found with id {reminder_id}")
    return f"Cancelled reminder {reminder_id}."
