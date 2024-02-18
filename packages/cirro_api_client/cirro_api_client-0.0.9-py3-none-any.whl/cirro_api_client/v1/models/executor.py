from enum import Enum


class Executor(str, Enum):
    CROMWELL = "CROMWELL"
    INGEST = "INGEST"
    NEXTFLOW = "NEXTFLOW"

    def __str__(self) -> str:
        return str(self.value)
