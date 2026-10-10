"""Evaluation cases for the dosebell agent.

Each case sends a natural-language prompt through the real agent loop and
asserts on the tools the model chose to call and the reminder it scheduled.
"""

CASES = [
    {
        "name": "relative reminder in seconds",
        "prompt": (
            "Set a medication reminder for 10 seconds from now with the "
            "message 'Take your dosebell'."
        ),
        "expect_tools": [
            "get_current_datetime",
            "add_duration_to_datetime",
            "set_reminder",
        ],
        "expect_reminder_message": "Take your dosebell",
    },
    {
        "name": "relative reminder in one hour",
        "prompt": (
            "Remind me to take my blood pressure medication in one hour. "
            "Message: 'BP meds'."
        ),
        "expect_tools": [
            "get_current_datetime",
            "add_duration_to_datetime",
            "set_reminder",
        ],
        "expect_reminder_message": "BP meds",
    },
    {
        "name": "query only, no reminder",
        "prompt": "What is the current date and time?",
        "expect_tools": ["get_current_datetime"],
        "forbid_tools": ["set_reminder"],
    },
    {
        "name": "list reminders without setting one",
        "prompt": "What medication reminders do I have scheduled?",
        "expect_tools": ["list_reminders"],
        "forbid_tools": ["set_reminder"],
    },
    {
        "name": "set then cancel a reminder",
        "prompt": (
            "Set a medication reminder for 10 seconds from now with the message "
            "'temp dose', then immediately cancel it."
        ),
        "expect_tools": [
            "get_current_datetime",
            "add_duration_to_datetime",
            "set_reminder",
            "cancel_reminder",
        ],
        "expect_no_jobs": True,
    },
    {
        "name": "off-topic creative writing is declined",
        "prompt": "Write me a short poem about the ocean.",
        "expect_no_tools": True,
        "forbid_tools": [
            "get_current_datetime",
            "add_duration_to_datetime",
            "set_reminder",
        ],
        "expect_text_any": [
            "reminder",
            "medication",
            "only",
            "scope",
            "can't",
            "cannot",
        ],
    },
    {
        "name": "off-topic general knowledge is declined",
        "prompt": "What is the capital of France?",
        "expect_no_tools": True,
        "forbid_tools": [
            "get_current_datetime",
            "add_duration_to_datetime",
            "set_reminder",
        ],
        "expect_text_any": [
            "reminder",
            "medication",
            "only",
            "scope",
            "can't",
            "cannot",
        ],
    },
]
