from agent_helper import add_user_message, add_assistant_message, text_from_message
from llm import chat
from tools import (
    get_current_datetime_tool,
    add_duration_to_datetime_tool,
    set_reminder_tool,
    list_reminders_tool,
    cancel_reminder_tool,
    run_tools,
)

TOOLS = [
    get_current_datetime_tool,
    add_duration_to_datetime_tool,
    set_reminder_tool,
    list_reminders_tool,
    cancel_reminder_tool,
]

SYSTEM_PROMPT = (
    "You are dosebell, a focused medication-reminder assistant invoked as a "
    "single command with a natural-language request. You help users create, "
    "list, and cancel medication reminders, and answer questions about the "
    "current date and time, using the provided tools. "
    "Do the work with tools rather than asking the user for parameters: resolve "
    "relative times (such as 'in 30 minutes' or 'tomorrow at 8am') with the "
    "datetime tools before setting a reminder, and look up a reminder's id with "
    "list_reminders before cancelling it. "
    "Stay strictly within this scope: if a request is unrelated to medication "
    "reminders or the date/time (for example coding, general knowledge, "
    "creative writing, or booking travel), politely decline and say you can "
    "only help with medication reminders. Never call a tool for an "
    "out-of-scope request."
)


def run_conversation(messages):
    while True:
        response = chat(messages, system=SYSTEM_PROMPT, tools=TOOLS)
        add_assistant_message(messages, response)

        text = text_from_message(response)
        if text:
            print(text)

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
