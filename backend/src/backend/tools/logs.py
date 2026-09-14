import json
import subprocess

from langchain_core.tools import tool


def run_command(command: list[str], timeout: int = 10) -> str:
    """Run a predefined system command safely and return its output."""

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

    if result.returncode != 0:
        return json.dumps({
            "error": result.stderr.strip() or "Command failed.",
            "return_code": result.returncode,
        })

    return result.stdout.strip()


@tool
def get_system_logs(lines: int = 100) -> str:
    """Get recent system-wide logs from systemd journal."""

    lines = max(1, min(lines, 500))

    output = run_command(
        [
            "journalctl",
            "-n",
            str(lines),
            "--no-pager",
            "--output",
            "short-iso",
        ]
    )

    return output or json.dumps([])


@tool
def search_logs(query: str, lines: int = 100) -> str:
    """Search recent system logs for a specific text pattern."""

    if not query.strip():
        return json.dumps({
            "error": "Search query cannot be empty."
        })

    lines = max(1, min(lines, 500))

    output = run_command(
        [
            "journalctl",
            "--no-pager",
            "--output",
            "short-iso",
            "-n",
            str(lines),
            "--grep",
            query,
        ]
    )

    return output or json.dumps([])


@tool
def get_kernel_logs(lines: int = 100) -> str:
    """Get recent kernel messages from the systemd journal."""

    lines = max(1, min(lines, 500))

    output = run_command(
        [
            "journalctl",
            "-k",
            "-n",
            str(lines),
            "--no-pager",
            "--output",
            "short-iso",
        ]
    )

    return output or json.dumps([])