from datetime import datetime
from typing import Any

import requests
from pytz import UTC
from .errors import ResponseError
from .types import ParticipantType, Conversation

API_BASE_URL = "https://api.gradient-labs.ai"
USER_AGENT = "Gradient Labs Python"


class Client:
    def __init__(self, *, api_key: str, base_url: str = API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def start_conversation(
        self,
        *,
        conversation_id: str,
        customer_id: str,
        channel: str,
        metadata: Any = None,
        timeout: int = None,
    ) -> Conversation:
        body = self._post(
            "conversations",
            {
                "id": conversation_id,
                "customer_id": customer_id,
                "channel": channel,
                "metadata": metadata,
            },
            timeout=timeout,
        )
        return Conversation.from_dict(body)

    def add_message(
        self,
        *,
        message_id: str,
        conversation_id: str,
        body: str,
        participant_id: str,
        participant_type: ParticipantType,
        created: datetime = None,
        timeout: int = None,
    ) -> None:
        if created is None:
            created = datetime.now()

        body = self._post(
            f"conversations/{conversation_id}/messages",
            {
                "id": message_id,
                "body": body,
                "participant_id": participant_id,
                "participant_type": participant_type,
                "created": UTC.localize(created).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            timeout=timeout,
        )

    def cancel_conversation(self, *, conversation_id: str, timeout: int = None) -> None:
        requests.put(
            f"{self.base_url}/conversations/{conversation_id}/cancel",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": USER_AGENT,
            },
            timeout=timeout,
        )

    def _post(self, path: str, body: Any, timeout: int = None):
        url = f"{self.base_url}/{path}"
        rsp = requests.post(
            url,
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": USER_AGENT,
            },
            timeout=timeout,
        )
        if rsp.status_code != 200:
            raise ResponseError(rsp)
        return rsp.json()
