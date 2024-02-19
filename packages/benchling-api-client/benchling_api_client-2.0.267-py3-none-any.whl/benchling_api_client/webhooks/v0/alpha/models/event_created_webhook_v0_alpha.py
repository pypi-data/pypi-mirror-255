from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.event_created_webhook_v0_alpha_type import EventCreatedWebhookV0AlphaType
from ..models.v2_assay_run_created_event import V2AssayRunCreatedEvent
from ..models.v2_assay_run_updated_fields_event import V2AssayRunUpdatedFieldsEvent
from ..models.v2_entity_registered_event import V2EntityRegisteredEvent
from ..models.v2_entry_created_event import V2EntryCreatedEvent
from ..models.v2_entry_updated_fields_event import V2EntryUpdatedFieldsEvent
from ..models.v2_entry_updated_review_record_event import V2EntryUpdatedReviewRecordEvent
from ..models.v2_request_created_event import V2RequestCreatedEvent
from ..models.v2_request_updated_fields_event import V2RequestUpdatedFieldsEvent
from ..models.v2_request_updated_status_event import V2RequestUpdatedStatusEvent
from ..models.v2_workflow_output_created_event import V2WorkflowOutputCreatedEvent
from ..models.v2_workflow_output_updated_fields_event import V2WorkflowOutputUpdatedFieldsEvent
from ..models.v2_workflow_task_created_event import V2WorkflowTaskCreatedEvent
from ..models.v2_workflow_task_group_created_event import V2WorkflowTaskGroupCreatedEvent
from ..models.v2_workflow_task_group_updated_watchers_event import V2WorkflowTaskGroupUpdatedWatchersEvent
from ..models.v2_workflow_task_updated_assignee_event import V2WorkflowTaskUpdatedAssigneeEvent
from ..models.v2_workflow_task_updated_fields_event import V2WorkflowTaskUpdatedFieldsEvent
from ..models.v2_workflow_task_updated_scheduled_on_event import V2WorkflowTaskUpdatedScheduledOnEvent
from ..models.v2_workflow_task_updated_status_event import V2WorkflowTaskUpdatedStatusEvent
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventCreatedWebhookV0Alpha")


@attr.s(auto_attribs=True, repr=False)
class EventCreatedWebhookV0Alpha:
    """  """

    _event: Union[
        V2AssayRunCreatedEvent,
        V2AssayRunUpdatedFieldsEvent,
        V2EntityRegisteredEvent,
        V2EntryCreatedEvent,
        V2EntryUpdatedFieldsEvent,
        V2EntryUpdatedReviewRecordEvent,
        V2RequestCreatedEvent,
        V2RequestUpdatedFieldsEvent,
        V2RequestUpdatedStatusEvent,
        V2WorkflowTaskGroupCreatedEvent,
        V2WorkflowTaskGroupUpdatedWatchersEvent,
        V2WorkflowTaskCreatedEvent,
        V2WorkflowTaskUpdatedAssigneeEvent,
        V2WorkflowTaskUpdatedScheduledOnEvent,
        V2WorkflowTaskUpdatedStatusEvent,
        V2WorkflowTaskUpdatedFieldsEvent,
        V2WorkflowOutputCreatedEvent,
        V2WorkflowOutputUpdatedFieldsEvent,
        UnknownType,
    ]
    _type: EventCreatedWebhookV0AlphaType
    _deprecated: bool
    _excluded_properties: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("event={}".format(repr(self._event)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("deprecated={}".format(repr(self._deprecated)))
        fields.append("excluded_properties={}".format(repr(self._excluded_properties)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EventCreatedWebhookV0Alpha({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self._event, UnknownType):
            event = self._event.value
        elif isinstance(self._event, V2AssayRunCreatedEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2AssayRunUpdatedFieldsEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2EntityRegisteredEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2EntryCreatedEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2EntryUpdatedFieldsEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2EntryUpdatedReviewRecordEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2RequestCreatedEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2RequestUpdatedFieldsEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2RequestUpdatedStatusEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskGroupCreatedEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskGroupUpdatedWatchersEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskCreatedEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskUpdatedAssigneeEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskUpdatedScheduledOnEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskUpdatedStatusEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowTaskUpdatedFieldsEvent):
            event = self._event.to_dict()

        elif isinstance(self._event, V2WorkflowOutputCreatedEvent):
            event = self._event.to_dict()

        else:
            event = self._event.to_dict()

        type = self._type.value

        deprecated = self._deprecated
        excluded_properties = self._excluded_properties

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if event is not UNSET:
            field_dict["event"] = event
        if type is not UNSET:
            field_dict["type"] = type
        if deprecated is not UNSET:
            field_dict["deprecated"] = deprecated
        if excluded_properties is not UNSET:
            field_dict["excludedProperties"] = excluded_properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_event() -> Union[
            V2AssayRunCreatedEvent,
            V2AssayRunUpdatedFieldsEvent,
            V2EntityRegisteredEvent,
            V2EntryCreatedEvent,
            V2EntryUpdatedFieldsEvent,
            V2EntryUpdatedReviewRecordEvent,
            V2RequestCreatedEvent,
            V2RequestUpdatedFieldsEvent,
            V2RequestUpdatedStatusEvent,
            V2WorkflowTaskGroupCreatedEvent,
            V2WorkflowTaskGroupUpdatedWatchersEvent,
            V2WorkflowTaskCreatedEvent,
            V2WorkflowTaskUpdatedAssigneeEvent,
            V2WorkflowTaskUpdatedScheduledOnEvent,
            V2WorkflowTaskUpdatedStatusEvent,
            V2WorkflowTaskUpdatedFieldsEvent,
            V2WorkflowOutputCreatedEvent,
            V2WorkflowOutputUpdatedFieldsEvent,
            UnknownType,
        ]:
            event: Union[
                V2AssayRunCreatedEvent,
                V2AssayRunUpdatedFieldsEvent,
                V2EntityRegisteredEvent,
                V2EntryCreatedEvent,
                V2EntryUpdatedFieldsEvent,
                V2EntryUpdatedReviewRecordEvent,
                V2RequestCreatedEvent,
                V2RequestUpdatedFieldsEvent,
                V2RequestUpdatedStatusEvent,
                V2WorkflowTaskGroupCreatedEvent,
                V2WorkflowTaskGroupUpdatedWatchersEvent,
                V2WorkflowTaskCreatedEvent,
                V2WorkflowTaskUpdatedAssigneeEvent,
                V2WorkflowTaskUpdatedScheduledOnEvent,
                V2WorkflowTaskUpdatedStatusEvent,
                V2WorkflowTaskUpdatedFieldsEvent,
                V2WorkflowOutputCreatedEvent,
                V2WorkflowOutputUpdatedFieldsEvent,
                UnknownType,
            ]
            _event = d.pop("event")

            if True:
                discriminator = _event["eventType"]
                if discriminator == "v2.assayRun.created":
                    event = V2AssayRunCreatedEvent.from_dict(_event)
                elif discriminator == "v2.assayRun.updated.fields":
                    event = V2AssayRunUpdatedFieldsEvent.from_dict(_event)
                elif discriminator == "v2.entity.registered":
                    event = V2EntityRegisteredEvent.from_dict(_event)
                elif discriminator == "v2.entry.created":
                    event = V2EntryCreatedEvent.from_dict(_event)
                elif discriminator == "v2.entry.updated.fields":
                    event = V2EntryUpdatedFieldsEvent.from_dict(_event)
                elif discriminator == "v2.entry.updated.reviewRecord":
                    event = V2EntryUpdatedReviewRecordEvent.from_dict(_event)
                elif discriminator == "v2.request.created":
                    event = V2RequestCreatedEvent.from_dict(_event)
                elif discriminator == "v2.request.updated.fields":
                    event = V2RequestUpdatedFieldsEvent.from_dict(_event)
                elif discriminator == "v2.request.updated.status":
                    event = V2RequestUpdatedStatusEvent.from_dict(_event)
                elif discriminator == "v2.workflowOutput.created":
                    event = V2WorkflowOutputCreatedEvent.from_dict(_event)
                elif discriminator == "v2.workflowOutput.updated.fields":
                    event = V2WorkflowOutputUpdatedFieldsEvent.from_dict(_event)
                elif discriminator == "v2.workflowTask.created":
                    event = V2WorkflowTaskCreatedEvent.from_dict(_event)
                elif discriminator == "v2.workflowTask.updated.assignee":
                    event = V2WorkflowTaskUpdatedAssigneeEvent.from_dict(_event)
                elif discriminator == "v2.workflowTask.updated.fields":
                    event = V2WorkflowTaskUpdatedFieldsEvent.from_dict(_event)
                elif discriminator == "v2.workflowTask.updated.scheduledOn":
                    event = V2WorkflowTaskUpdatedScheduledOnEvent.from_dict(_event)
                elif discriminator == "v2.workflowTask.updated.status":
                    event = V2WorkflowTaskUpdatedStatusEvent.from_dict(_event)
                elif discriminator == "v2.workflowTaskGroup.created":
                    event = V2WorkflowTaskGroupCreatedEvent.from_dict(_event)
                elif discriminator == "v2.workflowTaskGroup.updated.watchers":
                    event = V2WorkflowTaskGroupUpdatedWatchersEvent.from_dict(_event)
                else:
                    event = UnknownType(value=_event)

            return event

        try:
            event = get_event()
        except KeyError:
            if strict:
                raise
            event = cast(
                Union[
                    V2AssayRunCreatedEvent,
                    V2AssayRunUpdatedFieldsEvent,
                    V2EntityRegisteredEvent,
                    V2EntryCreatedEvent,
                    V2EntryUpdatedFieldsEvent,
                    V2EntryUpdatedReviewRecordEvent,
                    V2RequestCreatedEvent,
                    V2RequestUpdatedFieldsEvent,
                    V2RequestUpdatedStatusEvent,
                    V2WorkflowTaskGroupCreatedEvent,
                    V2WorkflowTaskGroupUpdatedWatchersEvent,
                    V2WorkflowTaskCreatedEvent,
                    V2WorkflowTaskUpdatedAssigneeEvent,
                    V2WorkflowTaskUpdatedScheduledOnEvent,
                    V2WorkflowTaskUpdatedStatusEvent,
                    V2WorkflowTaskUpdatedFieldsEvent,
                    V2WorkflowOutputCreatedEvent,
                    V2WorkflowOutputUpdatedFieldsEvent,
                    UnknownType,
                ],
                UNSET,
            )

        def get_type() -> EventCreatedWebhookV0AlphaType:
            _type = d.pop("type")
            try:
                type = EventCreatedWebhookV0AlphaType(_type)
            except ValueError:
                type = EventCreatedWebhookV0AlphaType.of_unknown(_type)

            return type

        try:
            type = get_type()
        except KeyError:
            if strict:
                raise
            type = cast(EventCreatedWebhookV0AlphaType, UNSET)

        def get_deprecated() -> bool:
            deprecated = d.pop("deprecated")
            return deprecated

        try:
            deprecated = get_deprecated()
        except KeyError:
            if strict:
                raise
            deprecated = cast(bool, UNSET)

        def get_excluded_properties() -> List[str]:
            excluded_properties = cast(List[str], d.pop("excludedProperties"))

            return excluded_properties

        try:
            excluded_properties = get_excluded_properties()
        except KeyError:
            if strict:
                raise
            excluded_properties = cast(List[str], UNSET)

        event_created_webhook_v0_alpha = cls(
            event=event,
            type=type,
            deprecated=deprecated,
            excluded_properties=excluded_properties,
        )

        event_created_webhook_v0_alpha.additional_properties = d
        return event_created_webhook_v0_alpha

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def event(
        self,
    ) -> Union[
        V2AssayRunCreatedEvent,
        V2AssayRunUpdatedFieldsEvent,
        V2EntityRegisteredEvent,
        V2EntryCreatedEvent,
        V2EntryUpdatedFieldsEvent,
        V2EntryUpdatedReviewRecordEvent,
        V2RequestCreatedEvent,
        V2RequestUpdatedFieldsEvent,
        V2RequestUpdatedStatusEvent,
        V2WorkflowTaskGroupCreatedEvent,
        V2WorkflowTaskGroupUpdatedWatchersEvent,
        V2WorkflowTaskCreatedEvent,
        V2WorkflowTaskUpdatedAssigneeEvent,
        V2WorkflowTaskUpdatedScheduledOnEvent,
        V2WorkflowTaskUpdatedStatusEvent,
        V2WorkflowTaskUpdatedFieldsEvent,
        V2WorkflowOutputCreatedEvent,
        V2WorkflowOutputUpdatedFieldsEvent,
        UnknownType,
    ]:
        if isinstance(self._event, Unset):
            raise NotPresentError(self, "event")
        return self._event

    @event.setter
    def event(
        self,
        value: Union[
            V2AssayRunCreatedEvent,
            V2AssayRunUpdatedFieldsEvent,
            V2EntityRegisteredEvent,
            V2EntryCreatedEvent,
            V2EntryUpdatedFieldsEvent,
            V2EntryUpdatedReviewRecordEvent,
            V2RequestCreatedEvent,
            V2RequestUpdatedFieldsEvent,
            V2RequestUpdatedStatusEvent,
            V2WorkflowTaskGroupCreatedEvent,
            V2WorkflowTaskGroupUpdatedWatchersEvent,
            V2WorkflowTaskCreatedEvent,
            V2WorkflowTaskUpdatedAssigneeEvent,
            V2WorkflowTaskUpdatedScheduledOnEvent,
            V2WorkflowTaskUpdatedStatusEvent,
            V2WorkflowTaskUpdatedFieldsEvent,
            V2WorkflowOutputCreatedEvent,
            V2WorkflowOutputUpdatedFieldsEvent,
            UnknownType,
        ],
    ) -> None:
        self._event = value

    @property
    def type(self) -> EventCreatedWebhookV0AlphaType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EventCreatedWebhookV0AlphaType) -> None:
        self._type = value

    @property
    def deprecated(self) -> bool:
        if isinstance(self._deprecated, Unset):
            raise NotPresentError(self, "deprecated")
        return self._deprecated

    @deprecated.setter
    def deprecated(self, value: bool) -> None:
        self._deprecated = value

    @property
    def excluded_properties(self) -> List[str]:
        """These properties have been dropped from the payload due to size."""
        if isinstance(self._excluded_properties, Unset):
            raise NotPresentError(self, "excluded_properties")
        return self._excluded_properties

    @excluded_properties.setter
    def excluded_properties(self, value: List[str]) -> None:
        self._excluded_properties = value
