from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.agent.stream import stream_agent_events
from backend.agent.graph import chatbot
from backend.api.schemas import ChatRequest


router = APIRouter(
    prefix="/api",
    tags=["API"],
)

@router.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify that the API is running.
    """
    return {"status": "ok"}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream VPSentinel agent events for a chat message."""

    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    events = stream_agent_events(
        chatbot,
        request.message,
        config,
    )

    return StreamingResponse(
        events,
        media_type="application/x-ndjson",
    )