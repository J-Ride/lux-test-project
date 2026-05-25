# Notes

## Architecture choice

I split the code into three files because each file has exactly one job. If I add a tool, I touch `tools.py`. If I change the tone or add context to the prompt, I touch `prompts.py`. The loop in `agent.py` hasn't changed since I wrote it, and I don't expect it to. A teammate can open any one of those files and understand it without reading the other two.

## One change with four more hours

I'd inject `datetime.date.today()` into the system prompt so the agent knows what day it is. Right now it can't flag jobs completing in the next 30 days unless Brad explicitly asks — it has no concept of "today." One line in `prompts.py` fixes that and makes the morning brief genuinely proactive instead of purely reactive.

## Ambiguity resolved

The brief didn't say what to do when someone passes an invalid filter value, so I made `filter` an enum of four valid options in the tool schema. The model picks from a defined list, and if anything slips past that, I return a clean error dict instead of raising an exception. The failure shows up in the output where Brad can see it, not as a silent crash.
