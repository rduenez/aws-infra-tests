"""
Unit tests for DTOs (Data Transfer Objects).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.application.dto import (
    CreateItemRequest,
    UpdateItemRequest,
    ItemResponse,
    ItemListResponse,
    CreateItemResponse,
    UpdateItemResponse,
    DeleteItemResponse,
    QueueItemRequest,
    QueueItemResponse,
)


class TestCreateItemRequest:
    """Tests for CreateItemRequest DTO."""

    def test_valid_full_request(self):
        """Test creating a valid request with all fields."""
        request = CreateItemRequest(
            name="Test Item",
            description="Test description",
            price=29.99,
            quantity=100,
        )

        assert request.name == "Test Item"
        assert request.description == "Test description"
        assert request.price == 29.99
        assert request.quantity == 100

    def test_valid_minimal_request(self):
        """Test creating a valid request with minimal fields."""
        request = CreateItemRequest(name="Minimal")

        assert request.name == "Minimal"
        assert request.description is None
        assert request.price is None
        assert request.quantity == 0

    def test_invalid_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            CreateItemRequest(name="")

    def test_invalid_name_too_long(self):
        """Test that name exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            CreateItemRequest(name="x" * 256)

    def test_invalid_negative_price(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValidationError):
            CreateItemRequest(name="Test", price=-10)

    def test_invalid_negative_quantity(self):
        """Test that negative quantity is rejected."""
        with pytest.raises(ValidationError):
            CreateItemRequest(name="Test", quantity=-5)

    def test_price_zero_is_valid(self):
        """Test that zero price is valid."""
        request = CreateItemRequest(name="Free Item", price=0)
        assert request.price == 0

    def test_quantity_zero_is_valid(self):
        """Test that zero quantity is valid (default)."""
        request = CreateItemRequest(name="Test")
        assert request.quantity == 0


class TestUpdateItemRequest:
    """Tests for UpdateItemRequest DTO."""

    def test_valid_partial_update(self):
        """Test creating a valid partial update request."""
        request = UpdateItemRequest(name="Updated Name")

        assert request.name == "Updated Name"
        assert request.description is None
        assert request.price is None
        assert request.quantity is None

    def test_valid_full_update(self):
        """Test creating a full update request."""
        request = UpdateItemRequest(
            name="Updated",
            description="New description",
            price=99.99,
            quantity=50,
        )

        assert request.name == "Updated"
        assert request.description == "New description"
        assert request.price == 99.99
        assert request.quantity == 50

    def test_empty_update_is_valid(self):
        """Test that empty update request is technically valid (handled by route)."""
        request = UpdateItemRequest()

        assert request.name is None
        assert request.description is None

    def test_invalid_negative_price(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValidationError):
            UpdateItemRequest(price=-10)


class TestItemResponse:
    """Tests for ItemResponse DTO."""

    def test_valid_response(self):
        """Test creating a valid item response."""
        response = ItemResponse(
            id=1,
            name="Test Item",
            description="Description",
            price=29.99,
            quantity=100,
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

        assert response.id == 1
        assert response.name == "Test Item"

    def test_from_attributes(self):
        """Test creating response from object attributes."""

        class MockItem:
            id = 1
            name = "Test"
            description = None
            price = 10.0
            quantity = 5
            created_at = None
            updated_at = None

        response = ItemResponse.model_validate(MockItem())
        assert response.id == 1
        assert response.name == "Test"


class TestItemListResponse:
    """Tests for ItemListResponse DTO."""

    def test_valid_list_response(self):
        """Test creating a valid list response."""
        items = [
            ItemResponse(id=1, name="Item 1", quantity=10),
            ItemResponse(id=2, name="Item 2", quantity=20),
        ]

        response = ItemListResponse(data=items, count=2)

        assert response.count == 2
        assert len(response.data) == 2

    def test_empty_list_response(self):
        """Test creating an empty list response."""
        response = ItemListResponse(data=[], count=0)

        assert response.count == 0
        assert response.data == []


class TestQueueItemRequest:
    """Tests for QueueItemRequest DTO."""

    def test_valid_request(self):
        """Test creating a valid queue request."""
        request = QueueItemRequest(
            name="Async Item",
            description="Created via queue",
            price=19.99,
            quantity=50,
        )

        assert request.name == "Async Item"
        assert request.price == 19.99

    def test_invalid_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            QueueItemRequest(name="")


class TestQueueItemResponse:
    """Tests for QueueItemResponse DTO."""

    def test_valid_response(self):
        """Test creating a valid queue response."""
        response = QueueItemResponse(message_id="msg-12345")

        assert response.message == "Item creation queued successfully"
        assert response.message_id == "msg-12345"

    def test_custom_message(self):
        """Test creating response with custom message."""
        response = QueueItemResponse(
            message="Custom message",
            message_id="msg-67890",
        )

        assert response.message == "Custom message"
