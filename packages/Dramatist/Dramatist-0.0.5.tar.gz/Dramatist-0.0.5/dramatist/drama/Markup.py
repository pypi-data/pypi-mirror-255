from dataclasses import dataclass


@dataclass
class Markup:
    start: int
    end: int
    type: str
