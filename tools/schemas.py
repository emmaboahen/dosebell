from anthropic.types import ToolParam

from tools.handlers import DATE_FORMAT

get_current_datetime_tool = ToolParam(
    {
        "name": "get_current_datetime",
        "description": "Returns the current date and time formatted according to the specified format",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": (
                        "A string specifying the format of the returned datetime. "
                        "Uses Python's strftime format codes. Defaults to "
                        f"'{DATE_FORMAT}' if omitted."
                    ),
                }
            },
            "required": [],
        },
    }
)

add_duration_to_datetime_tool = ToolParam(
    {
        "name": "add_duration_to_datetime",
        "description": "Adds a specified duration in seconds to a given datetime string and returns the new datetime formatted according to the specified format",
        "input_schema": {
            "type": "object",
            "properties": {
                "base_datetime_str": {
                    "type": "string",
                    "description": "The base datetime string to which the duration will be added. Must be in the format specified by date_format.",
                },
                "duration_seconds": {
                    "type": "number",
                    "description": "The duration in seconds to add to the base datetime.",
                },
                "date_format": {
                    "type": "string",
                    "description": (
                        "A string specifying the format of the returned datetime. "
                        "Uses Python's strftime format codes. Defaults to "
                        f"'{DATE_FORMAT}' if omitted."
                    ),
                },
            },
            "required": ["base_datetime_str", "duration_seconds"],
        },
    }
)

set_reminder_tool = ToolParam(
    {
        "name": "set_reminder",
        "description": "Sets a reminder for a specific time with a given message",
        "input_schema": {
            "type": "object",
            "properties": {
                "reminder_time_str": {
                    "type": "string",
                    "description": "The time for the reminder. Must be in the format specified by date_format.",
                },
                "reminder_message": {
                    "type": "string",
                    "description": "The message for the reminder.",
                },
                "date_format": {
                    "type": "string",
                    "description": (
                        "A string specifying the format of the reminder time. "
                        "Uses Python's strftime format codes. Defaults to "
                        f"'{DATE_FORMAT}' if omitted."
                    ),
                },
            },
            "required": ["reminder_time_str", "reminder_message"],
        },
    }
)

list_reminders_tool = ToolParam(
    {
        "name": "list_reminders",
        "description": "Lists all scheduled reminders with their ids, messages, and times. Use this to find the id of a reminder the user wants to cancel.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
)

cancel_reminder_tool = ToolParam(
    {
        "name": "cancel_reminder",
        "description": "Cancels a scheduled reminder by its id. Call list_reminders first if you do not know the id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reminder_id": {
                    "type": "string",
                    "description": "The id of the reminder to cancel.",
                }
            },
            "required": ["reminder_id"],
        },
    }
)
