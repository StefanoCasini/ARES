from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PortDTO:
    """
    The container of single host's ports information.
    """
    # 1. REQUIRED FIELDS FIRST (No default values)
    port: str
    state: str
    banner: str
    service: str
    source: str
    ttl: str
    reason: str
    cpes: List[str] = field(default_factory=list)

    # 2. OPTIONAL FIELDS LAST (Has default values)
    port_type: str = "unknown"
    command: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "port_type": self.port_type,
            "state": self.state,
            "banner": self.banner,
            "service": self.service,
            "source": self.source,
            "ttl": self.ttl,
            "reason": self.reason,
            "cpes": self.cpes,
            "command": self.command
        }