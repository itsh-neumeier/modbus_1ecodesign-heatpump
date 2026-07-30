"""Endpoint parsing helpers."""

from __future__ import annotations

from urllib.parse import urlsplit


def normalize_modbus_endpoint(host: str, port: int) -> tuple[str, int]:
    """Normalize host and port from either separate fields or host:port input."""
    host = host.strip()
    parsed_port = int(port)

    if "://" in host:
        parsed = urlsplit(host)
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port is not None:
            parsed_port = parsed.port
        return host, parsed_port

    if host.startswith("[") and "]" in host:
        host_part, _, port_part = host[1:].partition("]")
        if port_part.startswith(":") and port_part[1:].isdigit():
            parsed_port = int(port_part[1:])
        return host_part, parsed_port

    if host.count(":") == 1:
        host_part, port_part = host.rsplit(":", 1)
        if host_part and port_part.isdigit():
            return host_part.strip(), int(port_part)

    return host, parsed_port
