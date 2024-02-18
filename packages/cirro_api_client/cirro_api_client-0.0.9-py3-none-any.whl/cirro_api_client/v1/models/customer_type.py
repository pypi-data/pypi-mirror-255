from enum import Enum


class CustomerType(str, Enum):
    CONSORTIUM = "CONSORTIUM"
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"

    def __str__(self) -> str:
        return str(self.value)
