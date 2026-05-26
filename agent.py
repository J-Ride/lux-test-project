import sys
import json
import anthropic
from dotenv import load_dotenv
from tools import execute_tool, TOOLS
from prompts import get_system_prompt

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


def parse_question() -> str:
    """Return the user's question from argv or stdin, exiting if none provided."""
    question = " ".join(sys.argv[1:]).strip()
    if question:
        return question
    question = sys.stdin.read().strip()
    if question:
        return question
    print('Usage: python agent.py "<question>"', file=sys.stderr)
    sys.exit(1)


def build_tool_results(content: list) -> list[dict]:
    """Execute all tool_use blocks in content and return tool_result dicts."""
    results = []
    for block in content:
        if block.type == "tool_use":
            print(f"[tool] {block.name}({block.input})", file=sys.stderr)
            result = execute_tool(block.name, block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })
    return results


def run_agent(question: str) -> None:
    """Drive the agentic tool-use loop until the model returns end_turn."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=get_system_prompt(),
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = build_tool_results(response.content)
            messages.append({"role": "user", "content": tool_results})
            continue

        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")


def main() -> None:
    """Load env, parse the question, and run the agent."""
    load_dotenv()
    question = parse_question()
    run_agent(question)


if __name__ == "__main__":
    main()
