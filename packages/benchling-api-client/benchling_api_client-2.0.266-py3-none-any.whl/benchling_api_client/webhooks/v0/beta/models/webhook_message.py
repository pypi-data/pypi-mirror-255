from typing import Union

from ..extensions import UnknownType
from ..models.event_created_webhook_v0_beta import EventCreatedWebhookV0Beta
from ..models.lifecycle_activate_webhook_v0_beta import LifecycleActivateWebhookV0Beta
from ..models.lifecycle_configuration_update_webhook_v0_beta import LifecycleConfigurationUpdateWebhookV0Beta
from ..models.lifecycle_deactivate_webhook_v0_beta import LifecycleDeactivateWebhookV0Beta

WebhookMessage = Union[
    LifecycleActivateWebhookV0Beta,
    LifecycleDeactivateWebhookV0Beta,
    LifecycleConfigurationUpdateWebhookV0Beta,
    EventCreatedWebhookV0Beta,
    UnknownType,
]
