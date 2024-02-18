from enum import Enum


class GetLargeFileStorageConfigResponse200Type(str, Enum):
    AZUREBLOBSTORAGE = "AzureBlobStorage"
    S3STORAGE = "S3Storage"

    def __str__(self) -> str:
        return str(self.value)
