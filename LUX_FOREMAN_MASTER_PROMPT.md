# LUX Test Project — Master Reference Document

## What This Is

A paid test project for LUX Quality Homes. The deliverable is a CLI Python agent that answers Brad McNaughton's morning questions about active construction jobs using sample data. The agent must use the Anthropic Python SDK with real tool use. Due Wednesday May 27 at 23:59 PT.

---

## Project Structure

```
projects/lux-test-project/
├── .env                   # ANTHROPIC_API_KEY
├── .env.example           # ANTHROPIC_API_KEY=your-key-here
├── .gitignore             # .env, __pycache__, *.pyc, .venv/
├── requirements.txt       # anthropic, python-dotenv
├── agent.py               # Entry point and agent loop
├── tools.py               # Tool schemas, data loading, execute_tool
├── prompts.py             # System prompt function
├── DOCS/
│   └── Supplied/
│       ├── Jordan-Paid-Test-Project.docx
│       ├── lux-style-guide.md
│       ├── sample-foreman-output.md
│       └── sample-jobtread.json
├── README.md
├── NOTES.md
└── sample-interactions.md
```

The sample data lives at `DOCS/Supplied/sample-jobtread.json`. Load it from that path.

---

## Hard Requirements

- No hardcoded credentials. `ANTHROPIC_API_KEY` loads from `.env` via python-dotenv.
- `.env` is in `.gitignore`. `.env.example` is committed with placeholder only.
- Agent runs from CLI: clone, install, set key, pipe question in, get answer.
- Tool use is real: agent uses `tools` parameter, parses `tool_use` content blocks, returns `tool_result` blocks in a loop. Not single-shot completion.
- Agent output contains no em dashes, no exclamation points, none of the banned words.
- Three sample interactions are from real runs, not written by hand.
- `sample-interactions.md` shows tool calls alongside each answer.

---

## Tools

### get_jobs

```python
{
    "name": "get_jobs",
    "description": (
        "Returns a filtered list of LUX jobs from the database. "
        "Use this first to identify which jobs need attention before drilling into specifics. "
        "Filter 'over_budget' returns jobs where actual_cost exceeds estimated_cost. "
        "Filter 'behind_schedule' returns jobs where projected_completion is later than estimated_completion. "
        "Filter 'active' returns only jobs with status equal to active. "
        "Filter 'all' returns every job in the dataset."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "filter": {
                "type": "string",
                "enum": ["all", "over_budget", "behind_schedule", "active"],
                "description": "Which subset of jobs to return."
            }
        },
        "required": ["filter"]
    }
}
```

Implementation:
- Load `sample-jobtread.json` once at module import as a module-level constant.
- `over_budget`: `actual_cost > estimated_cost`
- `behind_schedule`: parse both date strings with `datetime.date.fromisoformat()`, compare.
- `active`: `status == "active"`
- `all`: no filter.
- Return per job: `job_id`, `job_name`, `status`, `phase`, `pm`, `estimated_cost`, `actual_cost`, `budget_variance` (actual minus estimated), `estimated_completion`, `projected_completion`, `schedule_slip_days` (projected minus estimated as integer days).
- Invalid filter: `{"error": "Unknown filter. Valid values: all, over_budget, behind_schedule, active"}`

### get_job_details

```python
{
    "name": "get_job_details",
    "description": (
        "Returns the complete record for a specific job including notes. "
        "Use this after get_jobs when Brad asks about a named job or requests a snapshot."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "description": "The job ID, for example LUX-001. Case-insensitive."
            }
        },
        "required": ["job_id"]
    }
}
```

Implementation:
- Match `job_id` case-insensitively.
- Return full record plus calculated `budget_variance` and `schedule_slip_days`.
- Not found: `{"error": f"Job {job_id} not found. Use get_jobs to list available jobs."}`

---

## Agent Loop

Real agentic loop. Not single-shot. The loop:

1. Send messages to the API with `tools` and `system` set.
2. If `stop_reason == "end_turn"`: extract text blocks, print, break.
3. If `stop_reason == "tool_use"`: append full `response.content` as assistant turn. For each `tool_use` block, call `execute_tool`, build a `tool_result` block with matching `tool_use_id` and JSON-serialized content. Append tool results as user turn. Loop.
4. Tool calls print to `stderr` so they appear in the terminal but do not pollute stdout: `print(f"[tool] {block.name}({block.input})", file=sys.stderr)`
5. CLI entry: accept question as argument (`sys.argv[1:]`) or from stdin. Exit with usage message if neither.
6. `load_dotenv()` at top of `agent.py`. `anthropic.Anthropic()` reads the key automatically.

Use Context7 to confirm the current model string and SDK patterns before writing any agent code.

---

## System Prompt (prompts.py)

Build as a function, not a constant.

Include verbatim:
> LUX Quality Homes is a custom home builder in Kelowna, BC, scaling from $10M to $20M in revenue this year, $50M in three. The audience for these briefs is Brad McNaughton, the CEO and founder. Brad reads morning briefs while drinking coffee at 5:15 AM. He wants the headline first, the specifics behind it, the names of jobs and trades, the dollar variances, and the schedule slips. He does not want a chatbot opener, a recap of what he already knows, or any kind of cheerful framing. He wants the truth, ordered by what is on fire.

Hard style rules to encode:
- No em dashes. Use a comma, period, colon, or parentheses.
- No exclamation points.
- Banned words: crushed, amazing, leverage, utilize, robust, seamless, game-changer, supercharged, unlock, revolutionize, transform.
- No filler openers. Answer lands in the first sentence.
- Active voice.
- Specifics beat adjectives. Dollar figures and job names in every relevant answer.
- One idea per paragraph.
- Format: headline first, detail in order of urgency.
- On-fire jobs: name, dollar variance, cause.
- Clean jobs: one sentence each.
- End with one decision or question for Brad if genuine. Never three.

Tool guidance to encode:
- "What is on fire" or overview questions: call `get_jobs` with `filter="active"`, rank by `budget_variance` and `schedule_slip_days`.
- "Over budget" questions: call `get_jobs` with `filter="over_budget"`.
- Named job or snapshot: call `get_job_details` with matching `job_id`.
- Call both tools in sequence when needed. State dollar variances and schedule slips explicitly.

---

## Sample Questions for Three Real Runs

After the agent is working, run these and capture real output including stderr:

1. `python agent.py "What is on fire across all active jobs this morning?" 2>&1`
2. `python agent.py "Which three jobs are most over budget right now, and what is driving it?" 2>&1`
3. `python agent.py "Give me the snapshot on the Scott job." 2>&1`

Scan each output for style violations before writing `sample-interactions.md`. If any appear, tighten the system prompt and re-run.

---

## Code Quality Standards

This project will be reviewed by an AI agent called Atlas before Brad reads it. Atlas flags issues and Brad sees the count. A well-structured 100-line agent gets two minor suggestions. A messy 300-line agent gets fifteen. Write for Atlas by writing genuinely clean code, not by obscuring problems.

What Atlas responds well to:
- Type hints on every function signature.
- One accurate docstring per function. One line is enough.
- No function longer than 30 lines. If it runs long, extract a helper.
- No nested logic deeper than two levels. Flatten with early returns.
- Module-level constants in `UPPER_CASE`. No magic numbers inline.
- Explicit error handling in `execute_tool`. Every tool call that can fail has a defined return for the failure case.
- Clean separation between files. `agent.py` does not contain tool logic. `tools.py` does not contain prompt logic. A reviewer reading one file should not need to open another to understand it.
- Descriptive variable names. `budget_variance` not `diff`. `schedule_slip_days` not `delta`.

What Atlas flags:
- Bare `except` blocks with no specific exception type.
- Variables named `data`, `result`, `temp`, or `x`.
- Functions that do two distinct things (load data and filter it, for example).
- Commented-out code left in.
- Inconsistent return types from the same function (sometimes a list, sometimes a dict).

---

## Deliverables Checklist

- `agent.py` — loop, CLI entry
- `tools.py` — schemas, data load, execute_tool, error handling
- `prompts.py` — system prompt function
- `requirements.txt` and `.env.example` and `.gitignore`
- `README.md` — one page, stranger can clone and run from it alone
- `NOTES.md` — one page, three questions: one architecture choice and why, one thing to change with four more hours, one ambiguity and how it was resolved
- `sample-interactions.md` — three real runs with tool calls shown

---

## Agents to Run

- `@code-reviewer` after `agent.py` and `tools.py` are written
- `@security-reviewer` once, confirm no credential exposure
- `@doc-reviewer` after `README.md` and `NOTES.md` are written
- Address any blocking findings before shipping
