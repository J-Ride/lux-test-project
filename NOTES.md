# Notes

## Architecture choice

`agent.py`, `tools.py`, and `prompts.py` are three separate files because each has one job. Adding a third tool is a `tools.py`-only change. Swapping the data source from JSON to a live API is a `tools.py`-only change. Updating the system prompt is a `prompts.py`-only change. The loop in `agent.py` stays unchanged across all of these. A reviewer can read any one file and understand it without reading the others.

## One change with four more hours

Add a date-aware context so the agent knows today's date and can surface jobs with projected completion dates within the next 30 days without being asked. As built, the agent has no awareness of when "today" is, so it cannot proactively flag jobs that are nearing completion or deadline. This would be a one-line addition to the system prompt (inject `datetime.date.today()`) and would make the briefings more useful for Brad without requiring him to ask the question.

## Ambiguity resolved

The brief did not specify how to handle the `filter` parameter when an unknown value is passed. Resolved by making the filter an enum of four valid values in the tool schema, so the model can only choose from defined options and the implementation returns a clean error dict (not an exception) for anything that bypasses that constraint. This means invalid inputs are visible in the output rather than causing a silent crash.
