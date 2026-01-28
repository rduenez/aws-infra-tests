"""
Unit tests for ORMItemRepository.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from src.domain.entities import Item
from src.infrastructure.database import ORMItemRepository, ItemModel


class TestORMItemRepository:
    """Tests for the SQLAlchemy ORM Item repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_session_factory(self, mock_session):
        """Create a mock session factory."""
        factory = MagicMock()

        # Make the factory return a context manager that yields the session
        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = mock_session
        context_manager.__aexit__.return_value = None
        factory.return_value = context_manager

        return factory

    @pytest.fixture
    def repository(self, mock_session_factory) -> ORMItemRepository:
        """Create repository with mocked session factory."""
        return ORMItemRepository(mock_session_factory)

    @pytest.mark.asyncio
    async def test_create_item(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test creating an item with ORM."""
        item = Item(
            name="Test Item",
            description="Test description",
            price=Decimal("29.99"),
            quantity=100,
        )

        # Mock refresh to set the ID
        async def mock_refresh(model):
            model.id = 1

        mock_session.refresh = mock_refresh

        result = await repository.create(item)

        assert result == 1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test getting an existing item by ID."""
        # Create mock model
        mock_model = MagicMock(spec=ItemModel)
        mock_model.id = 1
        mock_model.name = "Test Item"
        mock_model.description = "Description"
        mock_model.price = Decimal("29.99")
        mock_model.quantity = 100
        mock_model.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_model.updated_at = datetime(2024, 1, 15, 10, 30, 0)

        # Mock execute result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Item"
        assert result.price == Decimal("29.99")

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test getting a non-existent item by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test getting all items."""
        # Create mock models
        mock_model1 = MagicMock(spec=ItemModel)
        mock_model1.id = 1
        mock_model1.name = "Item 1"
        mock_model1.description = None
        mock_model1.price = Decimal("10.00")
        mock_model1.quantity = 10
        mock_model1.created_at = None
        mock_model1.updated_at = None

        mock_model2 = MagicMock(spec=ItemModel)
        mock_model2.id = 2
        mock_model2.name = "Item 2"
        mock_model2.description = None
        mock_model2.price = Decimal("20.00")
        mock_model2.quantity = 20
        mock_model2.created_at = None
        mock_model2.updated_at = None

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_model1, mock_model2]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test getting items when table is empty."""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_update(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test updating an item."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update(1, {"name": "Updated", "price": 39.99})

        assert result == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_empty_data(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test updating with empty data returns 0."""
        result = await repository.update(1, {})

        assert result == 0
        mock_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test updating a non-existent item."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.update(999, {"name": "Updated"})

        assert result == 0

    @pytest.mark.asyncio
    async def test_delete(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test deleting an item."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(1)

        assert result == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository: ORMItemRepository, mock_session: AsyncMock):
        """Test deleting a non-existent item."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result == 0


class TestItemModel:
    """Tests for the ItemModel ORM model."""

    def test_model_repr(self):
        """Test model string representation."""
        model = ItemModel(id=1, name="Test", price=Decimal("29.99"))

        repr_str = repr(model)

        assert "Item" in repr_str
        assert "id=1" in repr_str
        assert "Test" in repr_str

    def test_model_to_dict(self):
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
        assert result["quantity"] == 100
        assert result["created_at"] == "2024-01-15T10:30:00"

    def test_model_to_dict_with_none_values(self):
        """Test converting model with None values."""
        model = ItemModel(id=1, name="Test")

        result = model.to_dict()

        assert result["description"] is None
        assert result["price"] is None
