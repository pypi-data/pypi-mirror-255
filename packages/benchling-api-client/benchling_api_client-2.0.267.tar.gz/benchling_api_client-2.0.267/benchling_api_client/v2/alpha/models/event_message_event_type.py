from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EventMessageEventType(Enums.KnownString):
    V2_ASSAYRUNCREATED = "v2.assayRun.created"
    V2_ASSAYRUNUPDATEDFIELDS = "v2.assayRun.updated.fields"
    V2_ENTITYREGISTERED = "v2.entity.registered"
    V2_ENTRYCREATED = "v2.entry.created"
    V2_ENTRYUPDATEDFIELDS = "v2.entry.updated.fields"
    V2_ENTRYUPDATEDREVIEWRECORD = "v2.entry.updated.reviewRecord"
    V2_REQUESTCREATED = "v2.request.created"
    V2_REQUESTUPDATEDFIELDS = "v2.request.updated.fields"
    V2_REQUESTUPDATEDSTATUS = "v2.request.updated.status"
    V2_WORKFLOWTASKGROUPCREATED = "v2.workflowTaskGroup.created"
    V2_WORKFLOWTASKGROUPUPDATEDWATCHERS = "v2.workflowTaskGroup.updated.watchers"
    V2_WORKFLOWTASKCREATED = "v2.workflowTask.created"
    V2_WORKFLOWTASKUPDATEDASSIGNEE = "v2.workflowTask.updated.assignee"
    V2_WORKFLOWTASKUPDATEDSCHEDULEDON = "v2.workflowTask.updated.scheduledOn"
    V2_WORKFLOWTASKUPDATEDSTATUS = "v2.workflowTask.updated.status"
    V2_WORKFLOWTASKUPDATEDFIELDS = "v2.workflowTask.updated.fields"
    V2_WORKFLOWOUTPUTCREATED = "v2.workflowOutput.created"
    V2_WORKFLOWOUTPUTUPDATEDFIELDS = "v2.workflowOutput.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EventMessageEventType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EventMessageEventType must be a string (encountered: {val})")
        newcls = Enum("EventMessageEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EventMessageEventType, getattr(newcls, "_UNKNOWN"))
