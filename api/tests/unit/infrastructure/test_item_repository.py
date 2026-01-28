"""
Unit tests for MySQLItemRepository.
"""
import pytest
from unittest.mock import AsyncMock
from decimal import Decimal
from datetime import datetime

from src.domain.entities import Item
from src.infrastructure.database import MySQLItemRepository, DatabaseConnection


class TestMySQLItemRepository:
    """Tests for the MySQL Item repository implementation."""

    @pytest.fixture
    def repository(self, mock_db_connection: AsyncMock) -> MySQLItemRepository:
        """Create repository with mocked database connection."""
        return MySQLItemRepository(mock_db_connection)

    @pytest.mark.asyncio
    async def test_create_item_full(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test creating an item with all fields."""
        mock_db_connection.execute.return_value = 1

        item = Item(
            name="Test Item",
            description="Test description",
            price=Decimal("29.99"),
            quantity=100,
        )

        result = await repository.create(item)

        assert result == 1
        mock_db_connection.execute.assert_called_once()

        # Verify SQL contains all columns
        call_args = mock_db_connection.execute.call_args
        sql = call_args[0][0]
        assert "name" in sql
        assert "description" in sql
        assert "price" in sql
        assert "quantity" in sql

    @pytest.mark.asyncio
    async def test_create_item_minimal(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test creating an item with minimal fields."""
        mock_db_connection.execute.return_value = 2

        item = Item(name="Minimal Item")

        result = await repository.create(item)

        assert result == 2
        call_args = mock_db_connection.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]
        assert "name" in sql
        assert params == ("Minimal Item",)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test getting an existing item by ID."""
        mock_db_connection.fetch_one.return_value = {
            "id": 1,
            "name": "Test Item",
            "description": "Test description",
            "price": Decimal("29.99"),
            "quantity": 100,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Item"
        assert result.price == Decimal("29.99")
        mock_db_connection.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test getting a non-existent item by ID."""
        mock_db_connection.fetch_one.return_value = None

        result = await repository.get_by_id(999)

        assert result is None
        mock_db_connection.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test getting all items."""
        mock_db_connection.fetch_all.return_value = [
            {"id": 1, "name": "Item 1", "description": None, "price": Decimal("10.00"), "quantity": 10},
            {"id": 2, "name": "Item 2", "description": None, "price": Decimal("20.00"), "quantity": 20},
        ]

        result = await repository.get_all()

        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"
        mock_db_connection.fetch_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_limit(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test getting items with custom limit."""
        mock_db_connection.fetch_all.return_value = []

        await repository.get_all(limit=50)

        call_args = mock_db_connection.fetch_all.call_args
        params = call_args[0][1]
        assert params == (50,)

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test getting items when table is empty."""
        mock_db_connection.fetch_all.return_value = []

        result = await repository.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_update(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test updating an item."""
        mock_db_connection.execute.return_value = 1

        result = await repository.update(1, {"name": "Updated", "price": 39.99})

        assert result == 1
        call_args = mock_db_connection.execute.call_args
        sql = call_args[0][0]
        assert "UPDATE" in sql
        assert "name = %s" in sql
        assert "price = %s" in sql
        assert "WHERE id = %s" in sql

    @pytest.mark.asyncio
    async def test_update_empty_data(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test updating with empty data returns 0."""
        result = await repository.update(1, {})

        assert result == 0
        mock_db_connection.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test updating a non-existent item."""
        mock_db_connection.execute.return_value = 0

        result = await repository.update(999, {"name": "Updated"})

        assert result == 0

    @pytest.mark.asyncio
    async def test_delete(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test deleting an item."""
        mock_db_connection.execute.return_value = 1

        result = await repository.delete(1)

        assert result == 1
        call_args = mock_db_connection.execute.call_args
        sql = call_args[0][0]
        assert "DELETE FROM" in sql
        assert "WHERE id = %s" in sql

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository: MySQLItemRepository, mock_db_connection: AsyncMock):
        """Test deleting a non-existent item."""
        mock_db_connection.execute.return_value = 0

        result = await repository.delete(999)

        assert result == 0
