from abc import ABC, abstractmethod
from pathlib import Path

class CommandGenerator(ABC):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    @abstractmethod
    def generate_commands(self, config: dict) -> list:
        pass