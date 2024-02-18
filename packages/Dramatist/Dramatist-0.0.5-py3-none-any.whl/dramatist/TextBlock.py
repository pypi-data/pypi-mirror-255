from dataclasses import dataclass


@dataclass
class TextBlock:
    start_line: int
    end_line: int
    text: str
