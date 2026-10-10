# dosebell

An agentic medication reminder. You tell it in plain language when to take
your meds; the agent resolves the time and schedules the reminder through a
real scheduling backend, which delivers a native desktop notification when the
reminder fires (see [Notes](#notes-and-limitations) for how delivery works
today).

This is a proof of concept demonstrating **agentic development** with the
Anthropic API: a model-driven loop that reasons over user intent, decomposes
it into tool calls, and hands the result to a real scheduling backend.

## Demo

A ~4-minute screen recording of the agent handling requests end to end:

[Watch the demo](docs/dosebell-demo.mp4)

## How it works

There's a single command — `dosebell "<request>"` — and no flags or
subcommands to remember. The request goes into an agent loop against Claude,
which is given five tools and decides which to call and in what order:

| Tool | Purpose |
| --- | --- |
| `get_current_datetime` | Resolve "now" so relative times ("10 seconds from now") work |
| `add_duration_to_datetime` | Compute a future datetime from a base + duration |
| `set_reminder` | Persist a scheduled reminder and return a confirmation |
| `list_reminders` | Show scheduled reminders and their ids |
| `cancel_reminder` | Cancel a scheduled reminder by id |

For example, the request *"Set a medication reminder for 10 seconds from now"*
becomes:

```
get_current_datetime()            -> 2026-10-10 12:00:00
add_duration_to_datetime(...)     -> 2026-10-10 12:00:10
set_reminder(...)                 -> job id + confirmation
```

The model runs under a system prompt (`agent.SYSTEM_PROMPT`) that keeps it
strictly scoped to medication reminders and the date/time; off-topic requests
are politely declined without calling any tool.

When a reminder fires, delivery pops a modal macOS dialog via `osascript`
plus an `afplay` chime (`notify-send` on Linux, stdout elsewhere).
A dialog is used instead of `osascript`'s `display notification` because the
latter is attributed to Script Editor and is suppressed by default on many
machines (it fails silently, exiting 0).

```
┌──────────┐   request    ┌──────────┐   tools    ┌────────────────────┐
│  cli.py  │ ───────────► │ agent.py │ ─────────► │  llm.py (client)   │
│(dosebell)│              │  loop    │ ◄───────── │  Claude (Anthropic)│
└──────────┘              └────┬─────┘            └────────────────────┘
                               │ run_tools
                               ▼
                     ┌──────────────────────────┐
                     │ tools/ handlers + schemas │
                     └────────────┬─────────────┘
                                  │ set/list/cancel
                                  ▼
                        ┌───────────────────┐
                        │ reminders.py       │
                        │ APScheduler+SQLite │
                        └─────────┬─────────┘
                                  │ fires at run time
                                  ▼
                           desktop notification
```

## Project layout

```
dosebell/
├── cli.py             # entry point: `dosebell "<request>"` -> one agent turn
├── main.py            # thin shim so `python main.py` still works
├── agent.py           # the agent loop (tool-use orchestration)
├── llm.py             # transport layer: the only module aware of the SDK
├── reminders.py       # scheduling backend (APScheduler + persistent SQLite store)
├── agent_helper.py    # message helpers
├── tools/
│   ├── handlers.py    # tool implementations (pure logic)
│   ├── schemas.py     # ToolParam definitions sent to the model
│   └── runner.py      # dispatch + tool-result assembly
├── docs/
│   └── dosebell-demo.mp4   # screen recording of the agent in action
├── tests/             # pytest unit tests (no network)
├── evals/             # agent-behaviour evals (hits the real API)
├── conftest.py        # puts the project root on sys.path for pytest
├── pytest.ini         # test config
├── pyproject.toml     # packaging + the `dosebell` console script
├── requirements.txt
└── requirements-dev.txt
```

The modules are deliberately layered: `llm.py` knows about the Anthropic SDK,
`agent.py` knows about orchestration, `tools/` knows about capabilities, and
`reminders.py` knows about delivery. Nothing else does.

## Setup

```bash
python3 -m venv .venv         # use python3; macOS `python` is often Python 2
source .venv/bin/activate
pip install -e .
cp .env.example .env          # then add your ANTHROPIC_API_KEY
```

Run all commands below from the repository root.

## Usage

One command, in plain language. No flags or subcommands:

```bash
dosebell "remind me to take my blood pressure meds at 8am tomorrow"
dosebell "what reminders do I have scheduled?"
dosebell "cancel the reminder for my blood pressure meds"
```

The agent resolves times, calls the right tools, and prints what it did:

```
Reminder set for 2026-10-11 08:00:00: take my blood pressure meds (job id: 3f2a...)
```

## Tests

Unit tests cover the tool handlers, the agent loop, the tool dispatcher, the
CLI entry point, the message helpers, and the scheduler/notification layer.
They use fakes and monkeypatching, so they need no API key and no network:

```bash
pip install -r requirements-dev.txt
pytest
```

## Evals

The agent's *behaviour* (which tools it picks for a given prompt) is checked by
a small eval harness. These run against the real Anthropic API, so they need an
`ANTHROPIC_API_KEY` (e.g. in `.env`) and must be run from the repo root:

```bash
python -m evals.run_evals            # all cases
python -m evals.run_evals --limit 1  # just the first
```

Each case asserts the model calls the expected tools (as an ordered
subsequence), avoids forbidden tools, schedules a reminder with the right
message, or leaves no jobs behind (e.g. a "set it, then cancel it" prompt).
Scope cases feed off-topic prompts (creative writing, general knowledge) and
assert that the agent declines and calls **no** tools. Exit code is non-zero if
any case fails, so it can gate CI.

## Notes and limitations

- Each `dosebell` invocation is short-lived: it schedules (or lists/cancels)
  and exits. Reminders are persisted to a SQLite job store
  (`dosebell_jobs.sqlite`) that survives restarts, but nothing is running to
  deliver them at the scheduled instant. Today an overdue reminder fires the
  **next** time any `dosebell` command starts the scheduler, within a one-hour
  misfire grace window — a poor-man's catch-up, not true background delivery.
- Recurring schedules ("every day at 8am") are a natural next step: the
  `set_reminder` tool currently creates one-shot date triggers only.
- The Anthropic SDK version used here removed the `temperature` parameter;
  `llm.py` intentionally omits it.

## Roadmap

- Background delivery: a detached scheduler / launchd agent so reminders fire
  at the right time without a terminal open (closes the gap above)
- Recurring (cron-style) reminders via `CronTrigger`
