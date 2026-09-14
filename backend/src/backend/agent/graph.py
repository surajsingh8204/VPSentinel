from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from backend.agent.nodes import agent_node, tool_node
from backend.agent.state import AgentState
from backend.agent.stream import stream_agent_events


graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    tools_condition,
)

graph.add_edge("tools", "agent")


memory = MemorySaver()

chatbot = graph.compile(
    checkpointer=memory,
)


config = {
    "configurable": {
        "thread_id": "1",
    }
}


if __name__ == "__main__":
    while True:
        content = input("\nEnter your query or type exit() to exit: ")

        if content.lower() == "exit()":
            break

        for event in stream_agent_events(
            chatbot=chatbot,
            content=content,
            config=config,
        ):
            if event["type"] == "tool_call":
                print(f"\n🔧 {event['tool']}")

            elif event["type"] == "message":
                print(f"\n{event['content']}")