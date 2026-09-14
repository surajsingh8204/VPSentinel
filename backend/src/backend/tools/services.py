import json
import subprocess

from langchain_core.tools import tool


def run_command(command: list[str]) -> str:
    """Run a predefined system command and return its output."""

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0:
        return result.stderr.strip()

    return result.stdout.strip()


@tool
def list_failed_services() -> str:
    """List systemd services that are currently in a failed state."""

    output = run_command(
        [
            "systemctl",
            "--failed",
            "--no-legend",
            "--no-pager",
        ]
    )

    if not output:
        return json.dumps([])

    services = []

    for line in output.splitlines():
        parts = line.split()

        if len(parts) >= 2:
            services.append(parts[1])

    return json.dumps(services)


@tool
def get_service_status(service_name: str) -> str:
    """Get the current status of a specific systemd service."""

    return run_command(
        [
            "systemctl",
            "status",
            service_name,
            "--no-pager",
            "--full",
        ]
    )


@tool
def get_service_logs(service_name: str, lines: int = 100) -> str:
    """Get recent logs for a specific systemd service."""

    return run_command(
        [
            "journalctl",
            "-u",
            service_name,
            "-n",
            str(lines),
            "--no-pager",
        ]
    )