"""
Integration tests for queue endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.presentation.dependencies import Container


class TestQueueRoutes:
    """Tests for queue endpoints."""

    def test_queue_item_success(self, test_client: TestClient, mock_message_queue: AsyncMock):
        """Test queuing an item creation successfully."""
        mock_message_queue.send_message.return_value = "msg-id-12345"

        response = test_client.post("/queue", json={
            "name": "Async Item",
            "description": "Created via queue",
            "price": 29.99,
            "quantity": 50,
        })

        assert response.status_code == 202
        data = response.json()
        assert data["message"] == "Item creation queued successfully"
        assert data["message_id"] == "msg-id-12345"

    def test_queue_item_minimal(self, test_client: TestClient, mock_message_queue: AsyncMock):
        """Test queuing with minimal data."""
        mock_message_queue.send_message.return_value = "msg-id-67890"

        response = test_client.post("/queue", json={"name": "Minimal Async Item"})

        assert response.status_code == 202
        assert response.json()["message_id"] == "msg-id-67890"

    def test_queue_item_missing_name(self, test_client: TestClient):
        """Test queuing without required name field."""
        response = test_client.post("/queue", json={"description": "No name"})

        assert response.status_code == 422

    def test_queue_item_empty_name(self, test_client: TestClient):
        """Test queuing with empty name."""
        response = test_client.post("/queue", json={"name": ""})

        assert response.status_code == 422

    def test_queue_item_negative_price(self, test_client: TestClient):
        """Test queuing with negative price."""
        response = test_client.post("/queue", json={"name": "Test", "price": -10})

        assert response.status_code == 422

    def test_queue_item_sqs_error(self, test_client: TestClient, mock_message_queue: AsyncMock):
        """Test handling SQS errors."""
        mock_message_queue.send_message.side_effect = Exception("SQS connection failed")

        response = test_client.post("/queue", json={"name": "Test Item"})

        assert response.status_code == 500
        assert "Failed to queue message" in response.json()["detail"]

    def test_queue_item_verifies_message_format(self, test_client: TestClient, mock_message_queue: AsyncMock):
        """Test that the correct message format is sent to SQS."""
        mock_message_queue.send_message.return_value = "msg-id"

        test_client.post("/queue", json={
            "name": "Test Item",
            "description": "Test description",
            "price": 49.99,
            "quantity": 100,
        })

        # Verify the message structure sent to SQS
        call_args = mock_message_queue.send_message.call_args
        message = call_args[0][0]

        assert message["operation"] == "create"
        assert message["table"] == "items"
        assert message["data"]["name"] == "Test Item"
        assert message["data"]["description"] == "Test description"
        assert message["data"]["price"] == 49.99
        assert message["data"]["quantity"] == 100
