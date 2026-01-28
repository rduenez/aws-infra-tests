"""
Integration tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock


class TestHealthRoutes:
    """Tests for health check endpoints."""

    def test_health_check(self, test_client: TestClient):
        """Test the health check endpoint returns healthy status."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app_name"] == "Test CRUD API"
        assert data["version"] == "1.0.0-test"

    def test_readiness_check_success(self, test_client: TestClient, mock_db_connection: AsyncMock):
        """Test readiness check when database is available."""
        mock_db_connection.fetch_one.return_value = {"1": 1}

        response = test_client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    def test_readiness_check_db_error(self, test_client: TestClient, mock_db_connection: AsyncMock):
        """Test readiness check when database is unavailable."""
        mock_db_connection.fetch_one.side_effect = Exception("Connection refused")

        response = test_client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert "error" in data["database"]
