import argparse
import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

import agent
import reminders
import tools.runner as runner
from evals.cases import CASES

load_dotenv()


def is_subsequence(expected, actual):
    it = iter(actual)
    return all(item in it for item in expected)


def run_case(case):
    scheduler = BackgroundScheduler()
    scheduler.start()
    reminders._scheduler = scheduler

    recorded = []
    original_run_tool = runner.run_tool

    def spy(name, tool_input):
        recorded.append((name, tool_input))
        return original_run_tool(name, tool_input)

    error = None
    jobs = []
    messages = [{"role": "user", "content": case["prompt"]}]
    runner.run_tool = spy
    try:
        agent.run_conversation(messages)
        jobs = scheduler.get_jobs()
    except Exception as exc:  # noqa: BLE001
        error = exc
    finally:
        runner.run_tool = original_run_tool
        reminders._scheduler = None
        scheduler.shutdown(wait=False)

    tool_names = [name for name, _ in recorded]
    return evaluate(case, tool_names, jobs, error, assistant_reply(messages))


def assistant_reply(messages):
    for message in reversed(messages):
        if message["role"] == "assistant":
            return "\n".join(
                block.text
                for block in message["content"]
                if getattr(block, "type", None) == "text"
            )
    return ""


def evaluate(case, tool_names, jobs, error, reply):
    if error is not None:
        return False, f"raised {type(error).__name__}: {error}"

    if case.get("expect_no_tools") and tool_names:
        return False, f"expected no tools, but called {tool_names}"

    expected = case.get("expect_tools", [])
    if expected and not is_subsequence(expected, tool_names):
        return False, f"tools {tool_names} missing subsequence {expected}"

    for forbidden in case.get("forbid_tools", []):
        if forbidden in tool_names:
            return False, f"called forbidden tool '{forbidden}'"

    if case.get("expect_no_jobs") and jobs:
        return False, f"expected no scheduled jobs, found {[job.id for job in jobs]}"

    expected_message = case.get("expect_reminder_message")
    if expected_message is not None:
        scheduled = [job.args[0] for job in jobs if job.args]
        if expected_message not in scheduled:
            return False, f"scheduled {scheduled!r}, expected {expected_message!r}"

    expected_text = case.get("expect_text_any")
    if expected_text:
        lowered = reply.lower()
        if not any(term.lower() in lowered for term in expected_text):
            return False, f"reply stayed out of scope: {reply!r}"

    detail = "no tools called" if not tool_names else "tools " + " -> ".join(tool_names)
    return True, detail


def main():
    parser = argparse.ArgumentParser(description="Run dosebell agent evals")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set; skipping evals.")
        return 2

    cases = CASES[: args.limit] if args.limit else CASES
    failures = 0

    for case in cases:
        passed, detail = run_case(case)
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        print(f"[{status}] {case['name']}: {detail}")

    print(f"\n{len(cases) - failures}/{len(cases)} evals passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
