import socket

import psutil
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


@router.get("/metrics")
def get_metrics() -> dict:
    """Return current VPS resource usage and system information."""

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")

    return {
        # Current usage
        "cpu": round(psutil.cpu_percent(interval=0.2)),
        "memory": round(memory.percent),
        "storage": round(disk.percent),

        # System
        "hostname": socket.gethostname(),

        # CPU
        "cpu_cores": psutil.cpu_count(logical=True),
        "cpu_physical": psutil.cpu_count(logical=False),

        # RAM
        "memory_used": f"{memory.used / (1024 ** 2):.0f} MiB",
        "memory_total": f"{memory.total / (1024 ** 2):.0f} MiB",

        # Swap
        "swap_used": f"{swap.used / (1024 ** 2):.0f} MiB",
        "swap_total": f"{swap.total / (1024 ** 2):.1f} GiB",
        "swap_free": f"{swap.free / (1024 ** 2):.0f} MiB",
        "swap_percent": round(swap.percent, 1),

        # Disk
        "disk_used": f"{disk.used / (1000 ** 3):.1f} GB",
        "disk_total": f"{disk.total / (1000 ** 3):.1f} GB",
    }