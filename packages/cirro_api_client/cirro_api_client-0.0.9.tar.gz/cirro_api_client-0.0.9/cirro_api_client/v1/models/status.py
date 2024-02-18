from enum import Enum


class Status(str, Enum):
    ARCHIVED = "ARCHIVED"
    COMPLETED = "COMPLETED"
    DELETE = "DELETE"
    DELETED = "DELETED"
    DELETING = "DELETING"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"

    def __str__(self) -> str:
        return str(self.value)
