from enum import Enum


class AzureUserVer(str, Enum):
    VALUE_0 = "1.0"
    VALUE_1 = "2.0"

    def __str__(self) -> str:
        return str(self.value)
