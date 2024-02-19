from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EventCreatedWebhookV0AlphaType(Enums.KnownString):
    V0_ALPHAEVENTCREATED = "v0-alpha.event.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EventCreatedWebhookV0AlphaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EventCreatedWebhookV0AlphaType must be a string (encountered: {val})")
        newcls = Enum("EventCreatedWebhookV0AlphaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EventCreatedWebhookV0AlphaType, getattr(newcls, "_UNKNOWN"))
