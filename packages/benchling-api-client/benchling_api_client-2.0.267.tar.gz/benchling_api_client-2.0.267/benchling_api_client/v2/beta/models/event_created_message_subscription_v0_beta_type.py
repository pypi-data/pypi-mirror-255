from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EventCreatedMessageSubscriptionV0BetaType(Enums.KnownString):
    V0_BETAEVENTCREATED = "v0-beta.event.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EventCreatedMessageSubscriptionV0BetaType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of EventCreatedMessageSubscriptionV0BetaType must be a string (encountered: {val})"
            )
        newcls = Enum("EventCreatedMessageSubscriptionV0BetaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EventCreatedMessageSubscriptionV0BetaType, getattr(newcls, "_UNKNOWN"))
