from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields
from typing import Any, Dict


class ParticipantType(str, Enum):

    """A participant type identifies the type of user who has
    sent a message in a conversation."""

    CUSTOMER: str = "Customer"
    HUMAN_AGENT: str = "Agent"
    BOT: str = "Bot"


class ConversationChannel(str, Enum):

    """A channel identifies how the customer has gotten
    in touch with customer support."""

    EMAIL: str = "email"
    WEB: str = "web"


@dataclass_json
@dataclass(frozen=True)
class Conversation:

    """A conversation is the primary way that a customer
    talks to our AI agent.
    """

    id: str
    customer_id: str
    channel: str
    metadata: dict
    status: str
    created: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    updated: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )


@dataclass(frozen=True)
class WebhookConversation:
    """
    Details of the conversation the event relates to.
    """

    conversation_id: str = field(metadata=config(field_name="id"))
    """
    The conversation's assigned identifier.
    """

    customer_id: str
    """
    The customer's assigned identifier.
    """

    metadata: Any
    """
    Arbitrary metadata attached to the conversation.
    """


@dataclass_json
@dataclass(frozen=True)
class AgentMessageEvent:
    """
    An event that represents a message from the agent.
    """

    conversation: WebhookConversation
    """
    Details of the conversation the event relates to.
    """

    body: str
    """
    Text of the agent's message.
    """


@dataclass_json
@dataclass(frozen=True)
class ConversationHandOffEvent:
    conversation: WebhookConversation
    """
    Details of the conversation the event relates to.
    """


@dataclass_json
@dataclass(frozen=True)
class ConversationFinishedEvent:
    conversation: WebhookConversation
    """
    Details of the conversation the event relates to.
    """


@dataclass_json
@dataclass(frozen=True)
class ActionExecuteEvent:
    conversation: WebhookConversation
    """
    Details of the conversation the event relates to.
    """

    action: str
    """
    The action's given identifier.
    """

    params: Dict[str, Any]
    """
    Parameters the agent has generated for this action.
    """


@dataclass_json
@dataclass(frozen=True)
class WebhookEvent:
    event_id: str = field(metadata=config(field_name="id"))
    """
    Unique identifier for this event.
    """

    event_type: str = field(metadata=config(field_name="type"))
    """
    Type of event (see: https://api-docs.gradient-labs.ai/#webhooks).
    """

    sequence_number: int
    """
    Sequential index of this event within the conversation (see: https://api-docs.gradient-labs.ai/#sequence-numbers).
    """

    timestamp: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat, mm_field=fields.DateTime(format="iso")
        )
    )
    """
    Time at which this event was generated.
    """

    data: Any
    """
    Event data
    """
