# LUX Foreman Agent

A CLI agent that answers Brad's morning questions about active LUX jobs. Built on the Anthropic Python SDK with real tool use: the agent picks the right tool, parses the response, calls a second tool if needed, then writes the answer in builder voice.

This is the mini Foreman described in the test brief. Same loop shape as a production agent, smaller scope, sample data.

---

## How it works

The agent runs a real agentic loop. It does not produce a single-shot completion.

1. Your question goes in as the first user message.
2. The agent decides which tool to call: `get_jobs` for an overview, `get_job_details` for a specific job.
3. The tool result comes back as a `tool_result` block. The agent reads it and either calls additional tools as needed across multiple turns or writes the answer.
4. The answer prints to stdout. Tool calls print to stderr so you can see the loop without it polluting the output.

Two tools are available:

**`get_jobs(filter)`** returns a filtered list of jobs. Valid filters: `active`, `over_budget`, `behind_schedule`, `all`. Each result includes `budget_variance` (actual minus estimated) and `schedule_slip_days` (projected minus estimated) as calculated fields. Invalid filters return a clean error dict, not a crash.

**`get_job_details(job_id)`** returns the full record for one job including notes. Case-insensitive match. Not-found returns a clean error dict.

The system prompt contains the LUX context paragraph and all Hard Style Rules from the style guide. No em dashes. No hype words. Answer lands in the first sentence.

---

## Prerequisites

- Python 3.10+
- pip
- An Anthropic API key

On Windows, use the full path to `python.exe` if bare commands fail: `C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe`

---

## Setup

```bash
git clone https://github.com/J-Ride/lux-test-project
cd lux-test-project
cp .env.example .env
# Open .env and set: ANTHROPIC_API_KEY=your-key-here
pip install -r requirements.txt
```

---

## Run

```bash
python agent.py "What is on fire across all active jobs this morning?"
python agent.py "Which three jobs are most over budget right now, and what is driving it?"
python agent.py "Give me the snapshot on the Scott job."
```

Pass the question as an argument or pipe it via stdin:

```bash
echo "Give me the snapshot on the Scott job." | python agent.py
```

To see tool calls alongside the answer:

```bash
# bash / cmd
python agent.py "What is on fire across all active jobs this morning?" 2>&1

# PowerShell
python agent.py "What is on fire across all active jobs this morning?" *>&1
```

---

## File structure

```
agent.py               Entry point and agentic loop. No tool logic, no prompt logic.
tools.py               Tool schemas, data loading, filter logic, execute_tool dispatcher.
prompts.py             System prompt. Built from the LUX style guide and context paragraph.
requirements.txt       anthropic, python-dotenv
.env.example           API key template
DOCS/Supplied/         Sample data and style reference provided with the brief
README.md              This file
NOTES.md               Architecture decisions
sample-interactions.md Three real agent runs with tool calls captured
```

---

## Architecture

Three files, one job each.

`agent.py` owns the loop. `tools.py` owns data access and tool schemas. `prompts.py` owns the system prompt. Adding a third tool is a `tools.py`-only change. Swapping the data source from JSON to a live JobTread API is a `tools.py`-only change. The loop in `agent.py` stays unchanged across both.

The job data loads once at module import in `tools.py`, not on every tool call. `budget_variance` and `schedule_slip_days` are computed fields added at query time so the agent has specific numbers to pull from directly rather than doing arithmetic in the response.

Error handling: invalid filters return `{"error": "..."}` instead of raising exceptions. Unknown tool names in the dispatcher return an error dict. The JSON load at import is wrapped with `FileNotFoundError` and `json.JSONDecodeError` handling so a missing or malformed data file gives a clear message and exits before the agent loop starts.

---

## Sample interactions

See `sample-interactions.md` for three real runs including tool call output and final answers.
