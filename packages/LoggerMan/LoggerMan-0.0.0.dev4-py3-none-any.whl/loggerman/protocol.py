from typing import Protocol as _Protocol


class Stringable(_Protocol):

    def __str__(self) -> str:
        ...
