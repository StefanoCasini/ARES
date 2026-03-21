from dataclasses import dataclass, field
from typing import List

@dataclass
class OsDTO:
    """
    Represents an Operating System guess and the tools that identified it.
    """
    name: str                           # e.g., "Linux 4.x"
    command: str
    cpes: List[str] = field(default_factory=list)  # e.g., ["cpe:/o:linux:linux_kernel:4.15"]
    
    # You can even add accuracy later if you want!
    # accuracy: int = 100 

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cpes": self.cpes,
            "command": self.command
        }