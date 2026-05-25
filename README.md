# LUX Foreman Agent

A CLI and Claude Code subagent that answers Brad's morning questions about active LUX jobs in builder voice. Ask in plain English. Claude routes the question to the foreman, the agent pulls the data, returns the answer.

Built on the Anthropic Python SDK with real tool use: the agent picks the right tool, parses the response, calls a second tool if needed, then writes the answer in builder voice.

This is the mini Foreman described in the test brief. Same loop shape as a production agent, smaller scope, sample data.

---

## What this is

The brief asks for an agent that uses the Anthropic Python SDK with real tool use. That is the engine in `agent.py`: a true agentic loop, not single-shot completion. The agent picks the right tool, parses the result, calls another tool if needed, then writes the answer.

The brief also says LUX already runs production agents inside the platform. I built this the same way. The agent canbe implemented as a Claude Code subagent so it lives inside the environment Brad is already using. No terminal commands, no manual invocation, no switching tools. Ask a question, get the answer.

---

## Using it inside Claude Code

Open Claude Code in the project folder. The foreman subagent is already registered via `.claude/agents/foreman.md`.

Ask the question.

```
What is on fire across all active jobs this morning?
Which three jobs are most over budget right now?
Give me the snapshot on the Scott job.
```

Claude Code recognizes the question is about LUX jobs and routes it to the foreman subagent automatically. The agent calls the right tools against the sample dataset, then returns the answer in the same format as the sample morning brief Brad's team provided. Headline first. Job names, dollar variances, schedule slips. No filler, no opener, no hype words.

This is the production shape. A field user asks. The agent answers. Nothing else in the workflow.

---

## Using it from the terminal

The CLI is the backend the subagent calls into. It also stands alone.

```bash
python agent.py "Give me the snapshot on the Scott job."
```

To see the tool calls firing in real time alongside the answer:

```bash
# bash / cmd
python agent.py "Give me the snapshot on the Scott job." 2>&1

# PowerShell
python agent.py "Give me the snapshot on the Scott job." *>&1
```

Tool calls print to stderr. On Windows PowerShell, stderr displays in red. That is expected. It is the agent loop confirming which tool fired before writing the answer.

---

## What I built beyond the floor

The brief asks for a CLI agent. That is in here and it works. The brief does not ask for the agent to be installable as a Claude Code subagent. I added that because it matches what LUX is actually building. The production Foreman runs inside the platform, not as a manual terminal command. The submission should reflect that.

The agent runs three ways without changing the agent code:

**As a Claude Code subagent.** The primary interface. Ask in natural language inside Claude Code.

**As a CLI command.** `python agent.py "your question"` from the terminal. The same loop, the same tools, the same output. This is what powers a scheduled morning brief, a Make.com scenario, an n8n workflow, or a JobTread webhook.

**As a library.** Import `run_agent` from `agent.py` and call it from anywhere.

The agent code does not change between the three. The interface does. That separation is the point of the architecture.

---

## Setup

```bash
git clone https://github.com/J-Ride/lux-test-project
cd lux-test-project
cp .env.example .env
# Open .env and set: ANTHROPIC_API_KEY=your-key-here
pip install anthropic python-dotenv
```

Prerequisites: Python 3.10+, pip, an Anthropic API key.

On Windows, if `python` is not recognized after install, use the full path: `C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe` or disable the Microsoft Store Python alias in Settings.

---

## How the agent works

The agent runs a real agentic loop using the Anthropic Python SDK with tool use enabled.

1. The user question becomes the first user message.
2. The agent receives the system prompt, the tool schemas, and the message history. It decides which tool to call.
3. If the agent calls a tool, the response includes a `tool_use` content block. The loop appends the assistant turn to history, executes the tool, builds a `tool_result` block with the matching `tool_use_id`, and appends it as a user turn.
4. The loop continues until `stop_reason` is `end_turn`. The agent prints the final answer and exits.

The loop is capped at a maximum number of turns to prevent runaway calls if the API gets stuck.

Two tools are available:

**`get_jobs(filter)`** returns a filtered list of jobs. Valid filters: `active`, `over_budget`, `behind_schedule`, `all`. Each result includes `budget_variance` (actual minus estimated) and `schedule_slip_days` (projected minus estimated) as computed fields so the agent has the numbers ready to pull from. Invalid filters return a clean error dict, not an exception.

**`get_job_details(job_id)`** returns the full record for one job including notes. Case-insensitive match. Not-found returns a clean error dict.

The system prompt contains the LUX context paragraph and the Hard Style Rules from the style guide. No em dashes. No hype words. Answer lands in the first sentence. The sample morning brief from Brad's team is embedded as a few-shot example so the agent has a concrete voice reference, not abstract rules.

---

## Architecture

Three files, one job each. This is the part I care about most.

```
agent.py     The loop. No tool logic, no prompt logic.
tools.py     Tool schemas, data loading, filter logic, dispatcher.
prompts.py   System prompt. LUX context, style rules, tool guidance, few-shot example.
```

Adding a third tool is a `tools.py`-only change. Swapping the JSON data source for a live JobTread API is a `tools.py`-only change. Updating the system prompt is a `prompts.py`-only change. The loop in `agent.py` does not change in any of those cases.

The job data loads once at module import, not on every tool call. Computed fields are added at query time so the agent has the math done before it writes the answer. Error handling at every layer returns clean dicts instead of raising exceptions, so the agent can see and report failures rather than crashing.

This is how the production agent at LUX needs to be built if the goal is to add tools, swap data sources, and change interfaces without touching the loop. I built it that way from the start.

---

## File structure

```
agent.py                Entry point and agentic loop
tools.py                Tool schemas, data loading, execute_tool dispatcher
prompts.py              System prompt
.claude/agents/         The foreman Claude Code subagent
.env.example            API key template
DOCS/Supplied/          Sample data and style reference provided with the brief
README.md               This file
NOTES.md                Architecture decisions
sample-interactions.md  Three real agent runs with tool calls captured
```

---

## Sample interactions

See `sample-interactions.md` for three real runs. Each one shows the question, the tool calls fired, and the final answer in builder voice.

---

## Built by

Jordan Rideout for the LUX Quality Homes AI Software Engineer paid test project. May 2026.