"""
SQLAlchemy async session management.
"""
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Settings


class DatabaseSession:
    """
    Async database session manager using SQLAlchemy.

    Manages the engine and session factory lifecycle.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def _database_url(self) -> str:
        """Build the async database URL."""
        return (
            f"mysql+aiomysql://{self._settings.db_user}:{self._settings.db_password}"
            f"@{self._settings.db_host}:{self._settings.db_port}/{self._settings.db_name}"
        )

    async def connect(self) -> None:
        """Initialize the database engine and session factory."""
        if self._engine is None:
            self._engine = create_async_engine(
                self._database_url,
                echo=self._settings.debug,
                pool_size=self._settings.db_pool_min_size,
                max_overflow=self._settings.db_pool_max_size - self._settings.db_pool_min_size,
                pool_pre_ping=True,
            )
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

    async def disconnect(self) -> None:
        """Close the database engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async session.

        Yields:
            AsyncSession: A database session.
        """
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory."""
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory
