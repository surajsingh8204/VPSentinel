from collections.abc import Iterator
from typing import Any
import json


def extract_text(content: Any) -> str:
    """Normalize model message content into plain text."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))

        return "".join(text_parts)

    return str(content)


def stream_agent_events(chatbot: Any, content: str, config: dict) -> Iterator[str]:
    """Convert LangGraph events into NDJSON presentation events."""

    try:
        for event in chatbot.stream(
            {"messages": [{"role": "user", "content": content}]},
            config=config,
        ):
            node_output = event.get("agent")

            if not node_output:
                continue

            for message in node_output.get("messages", []):
                if message.type != "ai":
                    continue

                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        yield json.dumps({
                            "type": "tool_call",
                            "tool": tool_call["name"],
                        }) + "\n"
                    continue

                text = extract_text(message.content)

                if text.strip():
                    yield json.dumps({
                        "type": "message",
                        "content": text,
                    }) + "\n"

    except Exception:
        yield json.dumps({
            "type": "error",
            "message": "The agent encountered an error.",
        }) + "\n"