from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListConnectFilesDataType(Enums.KnownString):
    ALLOTROPE = "ALLOTROPE"
    GROUP = "GROUP"
    INJECTIONS = "INJECTIONS"
    MEASUREMENT = "MEASUREMENT"
    ORIGINAL = "ORIGINAL"
    PEAKS = "PEAKS"
    PROCESSED = "PROCESSED"
    SAMPLE = "SAMPLE"
    STATISTICS = "STATISTICS"
    WELL = "WELL"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListConnectFilesDataType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListConnectFilesDataType must be a string (encountered: {val})")
        newcls = Enum("ListConnectFilesDataType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListConnectFilesDataType, getattr(newcls, "_UNKNOWN"))
