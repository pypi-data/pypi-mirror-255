from enum import Enum


class ProjectRole(str, Enum):
    ADMIN = "ADMIN"
    COLLABORATOR = "COLLABORATOR"
    CONTRIBUTOR = "CONTRIBUTOR"
    NONE = "NONE"

    def __str__(self) -> str:
        return str(self.value)
