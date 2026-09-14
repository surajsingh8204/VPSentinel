from collections.abc import Iterator
from typing import Any


def stream_agent_events(
    chatbot: Any,
    content: str,
    config: dict,
) -> Iterator[dict]:
    """Convert LangGraph events into clean presentation events."""

    for event in chatbot.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        },
        config=config,
    ):
        for node_name, node_output in event.items():

            if node_name == "agent":
                for message in node_output.get("messages", []):
                    if message.type != "ai":
                        continue

                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            yield {
                                "type": "tool_call",
                                "tool": tool_call["name"],
                            }
                    else:
                        yield {
                            "type": "message",
                            "content": message.content,
                        }

            elif node_name == "tools":
                for message in node_output.get("messages", []):
                    yield {
                        "type": "tool_result",
                        "tool": message.name,
                    }