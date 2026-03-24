from dataclasses import dataclass, field
from typing import Any, Dict
from module.dtos.HostDTO import HostDTO

@dataclass
class FinalReportDTO:
    """
    The final report structure.
    """
    total_hosts: int
    commands: list[str] = field(default_factory=list)
    hosts: Dict[str, HostDTO] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "total_hosts": self.total_hosts,
            "commands": self.commands,
            "hosts": {ip: host.to_dict() for ip, host in self.hosts.items()}
        }