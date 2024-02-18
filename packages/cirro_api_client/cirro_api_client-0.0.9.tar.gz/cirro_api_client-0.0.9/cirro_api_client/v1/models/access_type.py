from enum import Enum


class AccessType(str, Enum):
    DATASET_UPLOAD = "DATASET_UPLOAD"
    PROJECT_DOWNLOAD = "PROJECT_DOWNLOAD"
    REFERENCE_UPLOAD = "REFERENCE_UPLOAD"
    SAMPLESHEET_UPLOAD = "SAMPLESHEET_UPLOAD"

    def __str__(self) -> str:
        return str(self.value)
