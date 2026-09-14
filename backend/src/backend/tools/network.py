import ipaddress
import json
import socket

import psutil
import requests

from langchain_core.tools import tool


def is_private_or_local_ip(ip_address: str) -> bool:
    """Check whether an IP address belongs to a private or local network."""

    ip = ipaddress.ip_address(ip_address)

    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def resolve_hostname(hostname: str) -> list[str]:
    """Resolve a hostname into unique IP addresses."""

    addresses = set()

    for result in socket.getaddrinfo(
        hostname,
        None,
        type=socket.SOCK_STREAM,
    ):
        addresses.add(result[4][0])

    return list(addresses)


@tool
def check_port(host: str, port: int) -> str:
    """Check whether a TCP port is reachable on a host."""

    if not 1 <= port <= 65535:
        return json.dumps({
            "error": "Port must be between 1 and 65535."
        })

    try:
        with socket.create_connection(
            (host, port),
            timeout=3,
        ):
            return json.dumps({
                "host": host,
                "port": port,
                "reachable": True,
            })

    except (OSError, socket.timeout) as exc:
        return json.dumps({
            "host": host,
            "port": port,
            "reachable": False,
            "error": str(exc),
        })


@tool
def check_url(url: str) -> str:
    """Check whether an HTTP or HTTPS URL is reachable."""

    if not url.startswith(("http://", "https://")):
        return json.dumps({
            "error": "Only HTTP and HTTPS URLs are allowed."
        })

    try:
        hostname = socket.gethostbyname(
            requests.utils.urlparse(url).hostname
        )

        if is_private_or_local_ip(hostname):
            return json.dumps({
                "error": "Requests to private or local network addresses are blocked."
            })

        response = requests.get(
            url,
            timeout=5,
            allow_redirects=False,
        )

        return json.dumps({
            "url": url,
            "status_code": response.status_code,
            "reachable": True,
        })

    except Exception as exc:
        return json.dumps({
            "url": url,
            "reachable": False,
            "error": str(exc),
        })


@tool
def get_listening_ports() -> str:
    """List TCP and UDP ports currently listening on the VPS."""

    connections = psutil.net_connections(kind="inet")

    listening = []

    for connection in connections:
        if connection.status == psutil.CONN_LISTEN:
            listening.append({
                "protocol": "tcp" if connection.type == socket.SOCK_STREAM else "udp",
                "address": connection.laddr.ip if connection.laddr else None,
                "port": connection.laddr.port if connection.laddr else None,
                "pid": connection.pid,
            })

    listening.sort(
        key=lambda item: (
            item["port"] if item["port"] is not None else 0
        )
    )

    return json.dumps(listening)


@tool
def get_active_connections() -> str:
    """List active network connections on the VPS."""

    connections = psutil.net_connections(kind="inet")

    active = []

    for connection in connections:
        if connection.status != psutil.CONN_NONE:
            active.append({
                "protocol": "tcp" if connection.type == socket.SOCK_STREAM else "udp",
                "local_address": (
                    f"{connection.laddr.ip}:{connection.laddr.port}"
                    if connection.laddr
                    else None
                ),
                "remote_address": (
                    f"{connection.raddr.ip}:{connection.raddr.port}"
                    if connection.raddr
                    else None
                ),
                "status": connection.status,
                "pid": connection.pid,
            })

    return json.dumps(active)