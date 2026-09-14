from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from backend.agent.nodes import agent_node, tool_node
from backend.agent.state import AgentState


# Build the LangGraph workflow.
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")


# Keep conversation state in memory for the current process.
memory = MemorySaver()

chatbot = graph.compile(checkpointer=memory)