from dataclasses import dataclass, field
from typing import Any, Dict, Set, List

from module.dtos.OsDTO import OsDTO
from module.dtos.PortDTO import PortDTO


@dataclass
class HostDTO:
    """
    The container of single host's parsed information.
    """
    ip: str
    ports: Dict[str, List[PortDTO]] = field(default_factory=dict)  # Maps "port/protocol" to port details,
    hostnames: Dict[str, List[str]] = field(default_factory=dict)  # List of hostnames and their associated tools
    os: List[OsDTO] = field(default_factory=list)  # List of OS guesses (e.g. "Linux 3.x - 4.x")
    cpes: Dict[str, Set[str]] = field(default_factory=dict)  # Set of CPE strings (e.g. "cpe:/a:apache:http_server")
    discovery_commands: Set[str] = field(default_factory=set)  # Set of commands that produced this host's data

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "discovery_commands": list(self.discovery_commands),
            "hostnames": {hn: tools for hn, tools in self.hostnames.items()},
            "os": [os.to_dict() for os in self.os],
            "cpes": {cpe_key: list(t_set) for cpe_key, t_set in self.cpes.items()},
            "ports": {
                port_key: [p.to_dict() for p in port_list]
                for port_key, port_list in self.ports.items()
            }
        }