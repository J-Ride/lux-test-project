# lux-test-project

A CLI agent that answers LUX Quality Homes morning construction questions using the Anthropic API with real tool use.

## Prerequisites

- Python 3.10+
- pip

Python must be on your PATH. On Windows, use the full path to `python.exe` if the commands below fail (e.g. `C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe`).

## Setup

```
git clone <repo>
cd lux-test-project
cp .env.example .env
# Set ANTHROPIC_API_KEY=your-key-here in .env
pip install -r requirements.txt
```

## Run

```bash
python agent.py "What is on fire across all active jobs this morning?"
python agent.py "Which three jobs are most over budget right now, and what is driving it?"
python agent.py "Give me the snapshot on the Scott job."
```

## Capturing tool calls

Tool calls are written to stderr. To see them alongside the answer:

- **bash/cmd:** add `2>&1` to the end of the command
- **PowerShell:** add `*>&1` to the end of the command

Example (bash): `python agent.py "What is on fire?" 2>&1`

## Folder structure

```
agent.py          entry point and agent loop
tools.py          tool schemas, data loading, execute_tool
prompts.py        system prompt
requirements.txt  dependencies
.env.example      API key template (ANTHROPIC_API_KEY)
DOCS/Supplied/    sample job data and style reference
```
