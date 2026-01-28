"""
Unit tests for SQSMessageQueue.
"""
import pytest
from unittest.mock import MagicMock, patch
import json

from src.config import Settings
from src.infrastructure.messaging import SQSMessageQueue


class TestSQSMessageQueue:
    """Tests for the SQS message queue implementation."""

    @pytest.fixture
    def settings(self) -> Settings:
        """Test settings."""
        return Settings(
            aws_region="us-east-1",
            sqs_queue_url="https://sqs.us-east-1.amazonaws.com/123456789/test-queue",
        )

    @pytest.fixture
    def mock_boto_client(self):
        """Mock boto3 SQS client."""
        with patch("src.infrastructure.messaging.sqs_client.boto3") as mock_boto:
            mock_client = MagicMock()
            mock_boto.client.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def sqs_queue(self, settings: Settings, mock_boto_client: MagicMock) -> SQSMessageQueue:
        """Create SQS queue with mocked boto3."""
        return SQSMessageQueue(settings)

    @pytest.mark.asyncio
    async def test_send_message_success(self, sqs_queue: SQSMessageQueue, mock_boto_client: MagicMock):
        """Test sending a message successfully."""
        mock_boto_client.send_message.return_value = {
            "MessageId": "test-message-id-12345",
            "MD5OfMessageBody": "abc123",
        }

        message = {
            "operation": "create",
            "table": "items",
            "data": {"name": "Test Item", "price": 29.99},
        }

        result = await sqs_queue.send_message(message)

        assert result == "test-message-id-12345"
        mock_boto_client.send_message.assert_called_once()

        # Verify call arguments
        call_kwargs = mock_boto_client.send_message.call_args[1]
        assert call_kwargs["QueueUrl"] == "https://sqs.us-east-1.amazonaws.com/123456789/test-queue"
        assert json.loads(call_kwargs["MessageBody"]) == message
        assert call_kwargs["MessageAttributes"]["Operation"]["StringValue"] == "create"

    @pytest.mark.asyncio
    async def test_send_message_with_default_operation(self, sqs_queue: SQSMessageQueue, mock_boto_client: MagicMock):
        """Test sending a message without operation defaults to 'create'."""
        mock_boto_client.send_message.return_value = {"MessageId": "msg-id"}

        message = {"table": "items", "data": {"name": "Test"}}

        await sqs_queue.send_message(message)

        call_kwargs = mock_boto_client.send_message.call_args[1]
        assert call_kwargs["MessageAttributes"]["Operation"]["StringValue"] == "create"

    @pytest.mark.asyncio
    async def test_send_message_custom_operation(self, sqs_queue: SQSMessageQueue, mock_boto_client: MagicMock):
        """Test sending a message with custom operation."""
        mock_boto_client.send_message.return_value = {"MessageId": "msg-id"}

        message = {"operation": "update", "data": {"name": "Test"}}

        await sqs_queue.send_message(message)

        call_kwargs = mock_boto_client.send_message.call_args[1]
        assert call_kwargs["MessageAttributes"]["Operation"]["StringValue"] == "update"

    def test_client_initialization(self, settings: Settings):
        """Test that boto3 client is initialized with correct region."""
        with patch("src.infrastructure.messaging.sqs_client.boto3") as mock_boto:
            SQSMessageQueue(settings)

            mock_boto.client.assert_called_once_with(
                "sqs",
                region_name="us-east-1",
            )
