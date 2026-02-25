from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ParsedDataDTO:
    """
    The top-level container for a parsed tool output
    """
    tool_name: str
    command: str

    # 'data' maps the IP address (str) to the host's parsed information.
    # We use 'Any' for now until we build the HostDTO for the inner layer.
    #TODO: replace Any with HostDTO once we have it defined. 
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "command": self.command,
            "data": self.data
        }