import json
import logging

from tools.handlers import (
    get_current_datetime,
    add_duration_to_datetime,
    set_reminder,
    list_reminders,
    cancel_reminder,
)

logger = logging.getLogger(__name__)


def run_tool(tool_name: str, tool_input: dict):
    logger.debug("Executing tool '%s' with inputs %s", tool_name, tool_input)
    match tool_name:
        case "get_current_datetime":
            return get_current_datetime(**tool_input)
        case "add_duration_to_datetime":
            return add_duration_to_datetime(**tool_input)
        case "set_reminder":
            return set_reminder(**tool_input)
        case "list_reminders":
            return list_reminders()
        case "cancel_reminder":
            return cancel_reminder(**tool_input)
        case _:
            raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message):
    tool_requests = [
        block for block in message.content if block.type == "tool_use"
    ]
    tool_result_blocks = []

    for tool_request in tool_requests:
        tool_name = tool_request.name
        tool_input = tool_request.input

        try:
            result = run_tool(tool_name, tool_input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps(result),
                    "is_error": False,
                }
            )
        except Exception as e:
            logger.exception("Error running tool '%s'", tool_name)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps({"error": str(e)}),
                    "is_error": True,
                }
            )

    return tool_result_blocks
