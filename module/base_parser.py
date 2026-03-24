from abc import ABC, abstractmethod
from pathlib import Path

from module.dtos.ParsedDataDTO import ParsedDataDTO

class BaseParser(ABC):
    
    @staticmethod
    @abstractmethod
    def can_handle(file_path: Path) -> bool:
        """
        Returns True if this parser recognizes the file.
        Checks extensions or specific file signatures.
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDataDTO:
        """
        Parses the file and returns a standardized dictionary.
        """
        pass