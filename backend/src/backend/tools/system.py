import json
import time

import psutil
from langchain_core.tools import tool

@tool
def get_cpu_usage() -> str:
    """Get the current CPU utilization of the VPS, including overall and per-core usage."""

    per_core_usage = psutil.cpu_percent(interval=1.0, percpu=True)

    result = {
        "overall_percent": sum(per_core_usage) / len(per_core_usage),
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "per_core_percent": per_core_usage,
    }

    return json.dumps(result)

@tool
def get_memory_usage() -> str:
    """Get the current RAM and swap memory usage of the VPS."""

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return json.dumps({
        "ram": {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "usage_percent": memory.percent,
        },
        "swap": {
            "total_bytes": swap.total,
            "used_bytes": swap.used,
            "free_bytes": swap.free,
            "usage_percent": swap.percent,
        },
    })

@tool
def get_disk_usage() -> str:
    """Get the disk usage of the root filesystem."""
    disk = psutil.disk_usage("/")

    return json.dumps({
        "total_bytes": disk.total,
        "used_bytes": disk.used,
        "free_bytes": disk.free,
        "usage_percent": disk.percent,
    })


@tool
def get_uptime() -> str:
    """Get how long the VPS has been running since the last boot."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    return json.dumps({
        "uptime_seconds": int(uptime_seconds)
    })


@tool
def get_load_average() -> str:
    """Get Linux load average for the last 1, 5, and 15 minutes, along with CPU capacity."""

    load_1, load_5, load_15 = psutil.getloadavg()

    logical_cpus = psutil.cpu_count(logical=True)

    result = {
        "load_average": {
            "1_minute": load_1,
            "5_minutes": load_5,
            "15_minutes": load_15,
        },
        "logical_cpu_count": logical_cpus,
    }

    return json.dumps(result)

@tool
def get_top_processes(limit: int = 5) -> str:
    """Get the processes currently consuming the most CPU."""

    limit = max(1, min(limit, 20))

    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "cmdline",
            "status",
            "memory_percent",
        ]
    ):
        try:
            cpu_percent = process.cpu_percent(interval=None)

            processes.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "username": process.info["username"],
                    "cpu_percent": cpu_percent,
                    "memory_percent": process.info["memory_percent"],
                    "status": process.info["status"],
                    "cmdline": " ".join(process.info["cmdline"] or []),
                }
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Give psutil a short measurement window so process CPU
    # percentages represent actual CPU activity.
    time.sleep(0.5)

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "cmdline",
            "status",
            "memory_percent",
        ]
    ):
        try:
            cpu_percent = process.cpu_percent(interval=None)

            for item in processes:
                if item["pid"] == process.info["pid"]:
                    item["cpu_percent"] = cpu_percent
                    break

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(
        key=lambda process: process["cpu_percent"] or 0,
        reverse=True,
    )

    return json.dumps(processes[:limit])