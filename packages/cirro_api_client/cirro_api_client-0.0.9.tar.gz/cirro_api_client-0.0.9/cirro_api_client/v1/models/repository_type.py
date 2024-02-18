from enum import Enum


class RepositoryType(str, Enum):
    AWS = "AWS"
    GITHUB_PRIVATE = "GITHUB_PRIVATE"
    GITHUB_PUBLIC = "GITHUB_PUBLIC"
    NONE = "NONE"

    def __str__(self) -> str:
        return str(self.value)
