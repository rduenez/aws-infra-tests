"""
Unit tests for ItemService.
"""
import pytest
from unittest.mock import AsyncMock
from decimal import Decimal
from datetime import datetime

from src.domain.services import ItemService
from src.infrastructure.database import ItemModel


class TestItemService:
    """Tests for the ItemService."""

    @pytest.mark.asyncio
    async def test_create_item(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test creating an item."""
        expected_item = ItemModel(
            id=1,
            name="New Item",
            description="Description",
            price=Decimal("29.99"),
            quantity=50,
        )
        mock_item_repository.create.return_value = expected_item

        result = await item_service.create_item(
            name="New Item",
            description="Description",
            price=29.99,
            quantity=50,
        )

        assert result.id == 1
        assert result.name == "New Item"
        mock_item_repository.create.assert_called_once_with(
            name="New Item",
            description="Description",
            price=29.99,
            quantity=50,
        )

    @pytest.mark.asyncio
    async def test_create_item_minimal(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test creating an item with minimal data."""
        expected_item = ItemModel(id=2, name="Minimal Item")
        mock_item_repository.create.return_value = expected_item

        result = await item_service.create_item(name="Minimal Item")

        assert result.id == 2
        mock_item_repository.create.assert_called_once_with(
            name="Minimal Item",
            description=None,
            price=None,
            quantity=0,
        )

    @pytest.mark.asyncio
    async def test_get_item_found(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_item_model: ItemModel):
        """Test getting an existing item."""
        mock_item_repository.get_by_id.return_value = sample_item_model

        result = await item_service.get_item(1)

        assert result == sample_item_model
        mock_item_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test getting a non-existent item."""
        mock_item_repository.get_by_id.return_value = None

        result = await item_service.get_item(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_items(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_item_models: list[ItemModel]):
        """Test getting all items."""
        mock_item_repository.get_all.return_value = sample_item_models

        result = await item_service.get_all_items()

        assert len(result) == 3
        mock_item_repository.get_all.assert_called_once_with(limit=100)

    @pytest.mark.asyncio
    async def test_get_all_items_with_limit(self, item_service: ItemService, mock_item_repository: AsyncMock, sample_item_models: list[ItemModel]):
        """Test getting items with custom limit."""
        mock_item_repository.get_all.return_value = sample_item_models[:2]

        result = await item_service.get_all_items(limit=2)

        assert len(result) == 2
        mock_item_repository.get_all.assert_called_once_with(limit=2)

    @pytest.mark.asyncio
    async def test_update_item(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test updating an item."""
        mock_item_repository.update.return_value = 1

        result = await item_service.update_item(1, name="Updated Name", price=39.99)

        assert result == 1
        mock_item_repository.update.assert_called_once_with(
            1,
            name="Updated Name",
            description=None,
            price=39.99,
            quantity=None,
        )

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, item_service: ItemService, mock_item_repository: AsyncMock):
        """Test updating a non-existent item."""
        mock_item_repository.update.return_value = 0

        result = await item_service.update_item(999, name="Updated")

        assert result == 0

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
