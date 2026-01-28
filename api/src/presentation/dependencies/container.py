"""
Dependency Injection Container.
"""
from typing import Optional

from src.config import Settings, get_settings
from src.domain.services import ItemService
from src.infrastructure.database import DatabaseSession, ItemRepository
from src.infrastructure.messaging import SQSMessageQueue


class Container:
    """
    Dependency Injection Container.

    Manages the lifecycle and dependencies of all application components.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._db_session: Optional[DatabaseSession] = None
        self._item_repository: Optional[ItemRepository] = None
        self._item_service: Optional[ItemService] = None
        self._message_queue: Optional[SQSMessageQueue] = None

    @property
    def settings(self) -> Settings:
        """Get application settings."""
        return self._settings

    @property
    def db_session(self) -> DatabaseSession:
        """Get database session manager."""
        if self._db_session is None:
            self._db_session = DatabaseSession(self._settings)
        return self._db_session

    @property
    def item_repository(self) -> ItemRepository:
        """Get item repository."""
        if self._item_repository is None:
            self._item_repository = ItemRepository(self.db_session.session_factory)
        return self._item_repository

    @property
    def item_service(self) -> ItemService:
        """Get item service."""
        if self._item_service is None:
            self._item_service = ItemService(self.item_repository)
        return self._item_service

    @property
    def message_queue(self) -> SQSMessageQueue:
        """Get message queue client."""
        if self._message_queue is None:
            self._message_queue = SQSMessageQueue(self._settings)
        return self._message_queue

    async def startup(self) -> None:
        """Initialize all connections on application startup."""
        await self.db_session.connect()

    async def shutdown(self) -> None:
        """Close all connections on application shutdown."""
        await self.db_session.disconnect()


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance (useful for testing)."""
    global _container
    _container = container
