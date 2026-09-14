import json

import docker
from langchain_core.tools import tool


def get_docker_client():
    """Create and return a Docker client connected to the local Docker daemon."""
    return docker.from_env()


@tool
def list_containers() -> str:
    """List all Docker containers on the VPS with their current status."""

    client = get_docker_client()
    containers = client.containers.list(all=True)

    result = [
        {
            "id": container.short_id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags,
        }
        for container in containers
    ]

    return json.dumps(result)


@tool
def inspect_container(container_name: str) -> str:
    """Inspect a Docker container and return its configuration and runtime details."""

    client = get_docker_client()
    container = client.containers.get(container_name)

    result = {
        "id": container.short_id,
        "name": container.name,
        "status": container.status,
        "image": container.image.tags,
        "ports": container.attrs["NetworkSettings"]["Ports"],
        "restart_policy": container.attrs["HostConfig"]["RestartPolicy"],
    }

    return json.dumps(result)


@tool
def get_container_stats(container_name: str) -> str:
    """Get current CPU and memory statistics for a Docker container."""

    client = get_docker_client()
    container = client.containers.get(container_name)

    stats = container.stats(stream=False)

    memory_usage = stats["memory_stats"].get("usage", 0)
    memory_limit = stats["memory_stats"].get("limit", 0)

    result = {
        "container": container.name,
        "cpu_stats": stats["cpu_stats"],
        "memory_usage_bytes": memory_usage,
        "memory_limit_bytes": memory_limit,
    }

    return json.dumps(result)


@tool
def get_container_logs(container_name: str, tail: int = 100) -> str:
    """Get recent logs from a Docker container."""

    client = get_docker_client()
    container = client.containers.get(container_name)

    logs = container.logs(
        tail=tail,
        timestamps=True,
    )

    return logs.decode(
        "utf-8",
        errors="replace",
    )


@tool
def list_images() -> str:
    """List Docker images available on the VPS."""

    client = get_docker_client()
    images = client.images.list()

    result = [
        {
            "id": image.short_id,
            "tags": image.tags,
            "size_bytes": image.attrs.get("Size"),
        }
        for image in images
    ]

    return json.dumps(result)