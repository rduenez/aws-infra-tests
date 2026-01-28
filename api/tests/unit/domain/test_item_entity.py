"""
Unit tests for Item entity.
"""
import pytest
from datetime import datetime
from decimal import Decimal

from src.domain.entities import Item


class TestItemEntity:
    """Tests for the Item domain entity."""

    def test_create_item_with_all_fields(self):
        """Test creating an item with all fields."""
        now = datetime.now()
        item = Item(
            id=1,
            name="Test Item",
            description="Test description",
            price=Decimal("29.99"),
            quantity=100,
            created_at=now,
            updated_at=now,
        )

        assert item.id == 1
        assert item.name == "Test Item"
        assert item.description == "Test description"
        assert item.price == Decimal("29.99")
        assert item.quantity == 100
        assert item.created_at == now
        assert item.updated_at == now

    def test_create_item_with_minimal_fields(self):
        """Test creating an item with only required fields."""
        item = Item(name="Minimal Item")

        assert item.id is None
        assert item.name == "Minimal Item"
        assert item.description is None
        assert item.price is None
        assert item.quantity == 0
        assert item.created_at is None
        assert item.updated_at is None

    def test_create_item_with_defaults(self):
        """Test creating an item with default values."""
        item = Item()

        assert item.id is None
        assert item.name == ""
        assert item.description is None
        assert item.price is None
        assert item.quantity == 0

    def test_to_dict(self):
        """Test converting item to dictionary."""
        now = datetime(2024, 1, 15, 10, 30, 0)
        item = Item(
            id=1,
            name="Test Item",
            description="Test description",
            price=Decimal("29.99"),
            quantity=100,
            created_at=now,
            updated_at=now,
        )

        result = item.to_dict()

        assert result["id"] == 1
        assert result["name"] == "Test Item"
        assert result["description"] == "Test description"
        assert result["price"] == 29.99
        assert result["quantity"] == 100
        assert result["created_at"] == "2024-01-15T10:30:00"
        assert result["updated_at"] == "2024-01-15T10:30:00"

    def test_to_dict_with_none_values(self):
        """Test converting item with None values to dictionary."""
        item = Item(id=1, name="Test Item")

        result = item.to_dict()

        assert result["id"] == 1
        assert result["name"] == "Test Item"
        assert result["description"] is None
        assert result["price"] is None
        assert result["quantity"] == 0
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_from_dict(self):
        """Test creating item from dictionary."""
        data = {
            "id": 1,
            "name": "Test Item",
            "description": "Test description",
            "price": 29.99,
            "quantity": 100,
        }

        item = Item.from_dict(data)

        assert item.id == 1
        assert item.name == "Test Item"
        assert item.description == "Test description"
        assert item.price == Decimal("29.99")
        assert item.quantity == 100

    def test_from_dict_with_minimal_data(self):
        """Test creating item from minimal dictionary."""
        data = {"name": "Minimal"}

        item = Item.from_dict(data)

        assert item.name == "Minimal"
        assert item.id is None
        assert item.price is None

    def test_from_dict_with_string_price(self):
        """Test creating item from dictionary with string price."""
        data = {
            "name": "Test Item",
            "price": "49.99",
        }

        item = Item.from_dict(data)

        assert item.price == Decimal("49.99")
