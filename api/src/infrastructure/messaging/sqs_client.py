import json
from typing import Any

import boto3

from src.application.interfaces import IMessageQueue
from src.config import Settings


class SQSMessageQueue(IMessageQueue):
    """AWS SQS implementation of the message queue interface."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

    async def send_message(self, message: dict[str, Any]) -> str:
        """
        Send a message to the SQS queue.

        Args:
            message: The message payload to send.

        Returns:
            The SQS message ID.
        """
        response = self._client.send_message(
            QueueUrl=self._settings.sqs_queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                "Operation": {
                    "DataType": "String",
                    "StringValue": message.get("operation", "create"),
                }
            },
        )
        return response["MessageId"]
