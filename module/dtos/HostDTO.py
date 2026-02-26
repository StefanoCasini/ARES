from dataclasses import dataclass, field
from typing import Any, Dict

from module.dtos.PortDTO import PortDTO


@dataclass
class HostDTO:
    """
    The container of single host's parsed information.
    """
    ip: str
    ports: Dict[str, PortDTO] = field(default_factory=dict)  # Maps "port/protocol" to port details,
    hostnames: list[str] = field(default_factory=list)  # List of hostnames associated with the IP
    os: list[str] = field(default_factory=list)  # List of OS guesses (e.g. "Linux 3.x - 4.x")
    cpes: list[str] = field(default_factory=list)  # List of CPE strings (e.g. "cpe:/a:apache:http_server")

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "ports": self.ports,
            "hostnames": self.hostnames,
            "os": self.os,
            "cpes": self.cpes
        }