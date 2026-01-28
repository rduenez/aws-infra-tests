"""
Unit tests for ItemService.
"""
import pytest
from unittest.mock import AsyncMock
from decimal import Decimal

from src.domain.entities import Item
from src.domain.services import ItemService


class TestItemService:
    """Tests for the ItemService domain service."""

    @pytest.mark.asyncio
    async def test_create_item(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test creating an item."""
        mock_item_repository.create.return_value = 1

        result = await item_service.create_item(
            name="New Item",
            description="New item description",
            price=29.99,
            quantity=50,
        )

        assert result == 1
        mock_item_repository.create.assert_called_once()

        # Verify the item passed to repository
        call_args = mock_item_repository.create.call_args
        created_item = call_args[0][0]
        assert created_item.name == "New Item"
        assert created_item.description == "New item description"
        assert created_item.price == 29.99
        assert created_item.quantity == 50

    @pytest.mark.asyncio
    async def test_create_item_minimal(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test creating an item with minimal data."""
        mock_item_repository.create.return_value = 2

        result = await item_service.create_item(name="Minimal Item")

        assert result == 2
        call_args = mock_item_repository.create.call_args
        created_item = call_args[0][0]
        assert created_item.name == "Minimal Item"
        assert created_item.description is None
        assert created_item.price is None
        assert created_item.quantity == 0

    @pytest.mark.asyncio
    async def test_get_item_found(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_item: Item):
        """Test getting an existing item."""
        mock_item_repository.get_by_id.return_value = sample_item

        result = await item_service.get_item(1)

        assert result == sample_item
        mock_item_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test getting a non-existent item."""
        mock_item_repository.get_by_id.return_value = None

        result = await item_service.get_item(999)

        assert result is None
        mock_item_repository.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_all_items(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_items: list[Item]):
        """Test getting all items."""
        mock_item_repository.get_all.return_value = sample_items

        result = await item_service.get_all_items()

        assert len(result) == len(sample_items)
        assert result == sample_items
        mock_item_repository.get_all.assert_called_once_with(limit=100)

    @pytest.mark.asyncio
    async def test_get_all_items_with_limit(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_items: list[Item]):
        """Test getting items with custom limit."""
        mock_item_repository.get_all.return_value = sample_items[:2]

        result = await item_service.get_all_items(limit=2)

        assert len(result) == 2
        mock_item_repository.get_all.assert_called_once_with(limit=2)

    @pytest.mark.asyncio
    async def test_update_item(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test updating an item."""
        mock_item_repository.update.return_value = 1

        result = await item_service.update_item(1, {"name": "Updated Name", "price": 39.99})

        assert result == 1
        mock_item_repository.update.assert_called_once_with(1, {"name": "Updated Name", "price": 39.99})

    @pytest.mark.asyncio
    async def test_update_item_filters_none_values(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test that update filters out None values."""
        mock_item_repository.update.return_value = 1

        result = await item_service.update_item(1, {"name": "Updated", "description": None})

        assert result == 1
        mock_item_repository.update.assert_called_once_with(1, {"name": "Updated"})

    @pytest.mark.asyncio
    async def test_update_item_empty_data(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test updating with empty data returns 0."""
        result = await item_service.update_item(1, {})

        assert result == 0
        mock_item_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_item_all_none_values(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test updating with all None values returns 0."""
        result = await item_service.update_item(1, {"name": None, "description": None})

        assert result == 0
        mock_item_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test deleting an item."""
        mock_item_repository.delete.return_value = 1

        result = await item_service.delete_item(1)

        assert result == 1
        mock_item_repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test deleting a non-existent item."""
        mock_item_repository.delete.return_value = 0

        result = await item_service.delete_item(999)

        assert result == 0
        mock_item_repository.delete.assert_called_once_with(999)
