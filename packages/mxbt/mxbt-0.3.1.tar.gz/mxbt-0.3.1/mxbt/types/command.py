from dataclasses import dataclass, field
from typing import List

@dataclass
class Command:

    prefix: str
    aliases: List[str]=field(
        default_factory=lambda: list()
    )

