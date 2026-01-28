"""
Integration tests for items CRUD endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from decimal import Decimal

from src.infrastructure.database import ItemModel


class TestCreateItem:
    """Tests for POST /items endpoint."""

    def test_create_item_success(self, test_client: TestClient, mock_item_repository: AsyncMock, sample_item_dict: dict):
        """Test creating an item successfully."""
        mock_item_repository.create.return_value = ItemModel(id=1, name=sample_item_dict["name"])

        response = test_client.post("/items", json=sample_item_dict)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Item created successfully"
        assert data["id"] == 1

    def test_create_item_minimal(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test creating an item with minimal data."""
        mock_item_repository.create.return_value = ItemModel(id=2, name="Minimal Item")

        response = test_client.post("/items", json={"name": "Minimal Item"})

        assert response.status_code == 201
        assert response.json()["id"] == 2

    def test_create_item_missing_name(self, test_client: TestClient):
        """Test creating an item without required name field."""
        response = test_client.post("/items", json={"description": "No name"})

        assert response.status_code == 422

    def test_create_item_empty_name(self, test_client: TestClient):
        """Test creating an item with empty name."""
        response = test_client.post("/items", json={"name": ""})

        assert response.status_code == 422

    def test_create_item_negative_price(self, test_client: TestClient):
        """Test creating an item with negative price."""
        response = test_client.post("/items", json={"name": "Test", "price": -10})

        assert response.status_code == 422


class TestGetItems:
    """Tests for GET /items endpoint."""

    def test_get_items_success(self, test_client: TestClient, mock_item_repository: AsyncMock, sample_item_models: list[ItemModel]):
        """Test getting all items."""
        mock_item_repository.get_all.return_value = sample_item_models

        response = test_client.get("/items")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == len(sample_item_models)

    def test_get_items_empty(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test getting items when none exist."""
        mock_item_repository.get_all.return_value = []

        response = test_client.get("/items")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["data"] == []

    def test_get_items_with_limit(self, test_client: TestClient, mock_item_repository: AsyncMock, sample_item_models: list[ItemModel]):
        """Test getting items with limit parameter."""
        mock_item_repository.get_all.return_value = sample_item_models[:2]

        response = test_client.get("/items?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2


class TestGetItemById:
    """Tests for GET /items/{item_id} endpoint."""

    def test_get_item_success(self, test_client: TestClient, mock_item_repository: AsyncMock, sample_item_model: ItemModel):
        """Test getting an item by ID."""
        mock_item_repository.get_by_id.return_value = sample_item_model

        response = test_client.get(f"/items/{sample_item_model.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_item_model.id
        assert data["name"] == sample_item_model.name

    def test_get_item_not_found(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test getting a non-existent item."""
        mock_item_repository.get_by_id.return_value = None

        response = test_client.get("/items/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateItem:
    """Tests for PUT /items/{item_id} endpoint."""

    def test_update_item_success(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test updating an item successfully."""
        mock_item_repository.update.return_value = 1

        response = test_client.put("/items/1", json={"name": "Updated Name"})

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item updated successfully"
        assert data["affected_rows"] == 1

    def test_update_item_not_found(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test updating a non-existent item."""
        mock_item_repository.update.return_value = 0

        response = test_client.put("/items/999", json={"name": "Updated"})

        assert response.status_code == 404

    def test_update_item_empty_body(self, test_client: TestClient):
        """Test updating with empty body."""
        response = test_client.put("/items/1", json={})

        assert response.status_code == 400
        assert "No fields provided" in response.json()["detail"]


class TestDeleteItem:
    """Tests for DELETE /items/{item_id} endpoint."""

    def test_delete_item_success(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test deleting an item successfully."""
        mock_item_repository.delete.return_value = 1

        response = test_client.delete("/items/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item deleted successfully"
        assert data["affected_rows"] == 1

    def test_delete_item_not_found(self, test_client: TestClient, mock_item_repository: AsyncMock):
        """Test deleting a non-existent item."""
        mock_item_repository.delete.return_value = 0

        response = test_client.delete("/items/999")

        assert response.status_code == 404
