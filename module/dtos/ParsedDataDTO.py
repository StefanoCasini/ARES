from dataclasses import dataclass, field
from typing import Any, Dict

from module.dtos.HostDTO import HostDTO


@dataclass
class ParsedDataDTO:
    """
    The top-level container for a parsed tool output
    """
    tool_name: str
    command: str

    # 'data' maps the IP address (str) to the host's parsed information.
    data: Dict[str, HostDTO] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "command": self.command,
            "data": self.data
        }