"""
Unit tests for ItemRepository.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime

from src.infrastructure.database import ItemRepository, ItemModel


class TestItemRepository:
    """Tests for the ItemRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        return AsyncMock()

    @pytest.fixture
    def mock_session_factory(self, mock_session):
        """Create a mock session factory."""
        factory = MagicMock()
        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = mock_session
        context_manager.__aexit__.return_value = None
        factory.return_value = context_manager
        return factory

    @pytest.fixture
    def repository(self, mock_session_factory) -> ItemRepository:
        """Create repository with mocked session factory."""
        return ItemRepository(mock_session_factory)

    @pytest.mark.asyncio
    async def test_create(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test creating an item."""
        async def mock_refresh(model):
            model.id = 1

        mock_session.refresh = mock_refresh

        result = await repository.create(
            name="Test Item",
            description="Test description",
            price=29.99,
            quantity=100,
        )

        assert result.id == 1
        assert result.name == "Test Item"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_minimal(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test creating an item with minimal data."""
        async def mock_refresh(model):
            model.id = 2

        mock_session.refresh = mock_refresh

        result = await repository.create(name="Minimal")

        assert result.name == "Minimal"
        assert result.description is None
        assert result.price is None

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test getting an existing item."""
        mock_model = ItemModel(
            id=1,
            name="Test Item",
            description="Description",
            price=Decimal("29.99"),
            quantity=100,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Item"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test getting a non-existent item."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test getting all items."""
        mock_models = [
            ItemModel(id=1, name="Item 1", quantity=10),
            ItemModel(id=2, name="Item 2", quantity=20),
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_models

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test getting items when table is empty."""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_update(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test updating an item."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update(1, name="Updated", price=39.99)

        assert result == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_filters_none(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test that update filters out None values."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update(1, name="Updated", description=None)

        assert result == 1

    @pytest.mark.asyncio
    async def test_update_empty_returns_zero(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test that update with no valid data returns 0."""
        result = await repository.update(1)

        assert result == 0
        mock_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test deleting an item."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(1)

        assert result == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository: ItemRepository, mock_session: AsyncMock):
        """Test deleting a non-existent item."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result == 0


class TestItemModel:
    """Tests for the ItemModel."""

    def test_repr(self):
        """Test model string representation."""
        model = ItemModel(id=1, name="Test", price=Decimal("29.99"))

        repr_str = repr(model)

        assert "Item" in repr_str
        assert "id=1" in repr_str

    def test_to_dict(self):
        """Test converting model to dictionary."""
        model = ItemModel(
            id=1,
            name="Test Item",
            description="Description",
            price=Decimal("29.99"),
            quantity=100,
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            updated_at=datetime(2024, 1, 15, 10, 30, 0),
        )

        result = model.to_dict()

        assert result["id"] == 1
        assert result["name"] == "Test Item"
        assert result["price"] == 29.99
        assert result["created_at"] == "2024-01-15T10:30:00"

    def test_to_dict_with_none(self):
        """Test converting model with None values."""
        model = ItemModel(id=1, name="Test")

        result = model.to_dict()

        assert result["description"] is None
        assert result["price"] is None
