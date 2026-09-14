from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from backend.agent.prompts import SYSTEM_PROMPT
from backend.llm.models import get_agent_model
from backend.tools import tools


llm = get_agent_model().bind_tools(tools)

tool_node = ToolNode(tools)


def agent_node(state: dict) -> dict:
    """Run the LLM and allow it to decide whether tools are needed."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm.invoke(messages)

    return {
        "messages": [response],
    }