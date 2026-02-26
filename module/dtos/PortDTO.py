from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PortDTO:
    """
    The container of single host's ports information.
    """
    port: str
    state: str
    banner: str
    service: str
    source: str
    ttl: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "state": self.state,
            "banner": self.banner,
            "service": self.service,
            "source": self.source,
            "ttl": self.ttl,
            "reason": self.reason
        }