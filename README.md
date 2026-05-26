# lux-test-project

A CLI agent that answers LUX Quality Homes morning construction questions using the Anthropic API with real tool use.

## Prerequisites

- Python 3.10+
- pip

## Setup

```
git clone <repo>
cd lux-test-project
cp .env.example .env
# Add your Anthropic API key to .env
pip install -r requirements.txt
```

## Run

```bash
python agent.py "What is on fire across all active jobs this morning?"
python agent.py "Which three jobs are most over budget right now, and what is driving it?"
python agent.py "Give me the snapshot on the Scott job."
```

## Capturing tool calls

Add `2>&1` to the end of any command to see tool calls alongside the answer in the terminal.

## Folder structure

```
agent.py          entry point and agent loop
tools.py          tool schemas, data loading, execute_tool
prompts.py        system prompt
requirements.txt  dependencies
.env.example      API key template
DOCS/Supplied/    sample job data and style reference
```
