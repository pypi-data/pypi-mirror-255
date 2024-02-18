from enum import Enum


class SyncStatus(str, Enum):
    FAILED = "FAILED"
    SUCCESSFUL = "SUCCESSFUL"

    def __str__(self) -> str:
        return str(self.value)
