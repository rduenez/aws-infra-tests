"""
Pytest configuration and shared fixtures.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from src.config import Settings
from src.domain.services import ItemService
from src.infrastructure.database import DatabaseSession, ItemRepository, ItemModel
from src.infrastructure.messaging import SQSMessageQueue
from src.presentation.dependencies import Container
from src.presentation.dependencies.container import set_container
from src.main import create_app


# =============================================================================
# Settings Fixtures
# =============================================================================

@pytest.fixture
def test_settings() -> Settings:
    """Test settings with mock values."""
    return Settings(
        app_name="Test CRUD API",
        app_version="1.0.0-test",
        debug=True,
        db_host="localhost",
        db_port=3306,
        db_user="test_user",
        db_password="test_password",
        db_name="test_db",
        db_pool_min_size=1,
        db_pool_max_size=5,
        aws_region="us-east-1",
        sqs_queue_url="https://sqs.us-east-1.amazonaws.com/123456789/test-queue",
    )


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_item_repository() -> AsyncMock:
    """Mock item repository."""
    repository = AsyncMock(spec=ItemRepository)
    return repository


@pytest.fixture
def mock_message_queue() -> AsyncMock:
    """Mock message queue."""
    queue = AsyncMock(spec=SQSMessageQueue)
    queue.send_message.return_value = "mock-message-id-12345"
    return queue


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock database session manager."""
    session = MagicMock(spec=DatabaseSession)
    session.connect = AsyncMock()
    session.disconnect = AsyncMock()

    # Mock session factory
    mock_async_session = AsyncMock()
    mock_factory = MagicMock()
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = mock_async_session
    context_manager.__aexit__.return_value = None
    mock_factory.return_value = context_manager
    session.session_factory = mock_factory

    return session


# =============================================================================
# Service Fixtures
# =============================================================================

@pytest.fixture
def item_service(mock_item_repository: AsyncMock) -> ItemService:
    """Item service with mocked repository."""
    return ItemService(mock_item_repository)


# =============================================================================
# Container Fixtures
# =============================================================================

@pytest.fixture
def mock_container(
    test_settings: Settings,
    mock_item_repository: AsyncMock,
    mock_message_queue: AsyncMock,
    mock_db_session: MagicMock,
) -> Container:
    """Mock DI container with all dependencies mocked."""
    container = Container(settings=test_settings)

    # Override with mocks
    container._db_session = mock_db_session
    container._item_repository = mock_item_repository
    container._item_service = ItemService(mock_item_repository)
    container._message_queue = mock_message_queue

    return container


# =============================================================================
# Test Client Fixtures
# =============================================================================

@pytest.fixture
def test_client(mock_container: Container) -> TestClient:
    """FastAPI test client with mocked dependencies."""
    set_container(mock_container)
    app = create_app()

    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_item_model() -> ItemModel:
    """Single sample ItemModel."""
    return ItemModel(
        id=1,
        name="Wireless Keyboard",
        description="Ergonomic wireless keyboard with backlit keys",
        price=Decimal("79.99"),
        quantity=150,
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_item_models() -> list[ItemModel]:
    """List of sample ItemModels."""
    return [
        ItemModel(
            id=1,
            name="Wireless Keyboard",
            description="Ergonomic wireless keyboard",
            price=Decimal("79.99"),
            quantity=150,
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            updated_at=datetime(2024, 1, 15, 10, 30, 0),
        ),
        ItemModel(
            id=2,
            name="USB-C Hub",
            description="7-in-1 USB-C hub",
            price=Decimal("49.99"),
            quantity=75,
            created_at=datetime(2024, 1, 16, 14, 20, 0),
            updated_at=datetime(2024, 1, 18, 9, 15, 0),
        ),
        ItemModel(
            id=3,
            name="Mechanical Mouse",
            description="Gaming mouse with RGB",
            price=Decimal("59.99"),
            quantity=200,
            created_at=datetime(2024, 1, 17, 8, 45, 0),
            updated_at=datetime(2024, 1, 17, 8, 45, 0),
        ),
    ]


@pytest.fixture
def sample_item_dict() -> dict:
    """Sample item as dictionary (for API requests)."""
    return {
        "name": "Wireless Keyboard",
        "description": "Ergonomic wireless keyboard with backlit keys",
        "price": 79.99,
        "quantity": 150,
    }
