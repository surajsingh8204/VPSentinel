from backend.tools.system import (
    get_cpu_usage,
    get_memory_usage,
    get_disk_usage,
    get_uptime,
    get_load_average,
    get_top_processes,
)

from backend.tools.docker import (
    list_containers,
    inspect_container,
    get_container_stats,
    get_container_logs,
    list_images,
)

from backend.tools.services import (
    list_failed_services,
    get_service_status,
    get_service_logs,
)

from backend.tools.network import (
    check_port,
    check_url,
    get_listening_ports,
    get_active_connections,
)

from backend.tools.logs import (
    get_system_logs,
    search_logs,
    get_kernel_logs,
)

from backend.tools.web import (
    web_search,
)


tools = [
    # System
    get_cpu_usage,
    get_memory_usage,
    get_disk_usage,
    get_uptime,
    get_load_average,
    get_top_processes,

    # Docker
    list_containers,
    inspect_container,
    get_container_stats,
    get_container_logs,
    list_images,

    # Services
    list_failed_services,
    get_service_status,
    get_service_logs,

    # Network
    check_port,
    check_url,
    get_listening_ports,
    get_active_connections,

    # Logs
    get_system_logs,
    search_logs,
    get_kernel_logs,

    # Web
    web_search,
]


__all__ = ["tools"]