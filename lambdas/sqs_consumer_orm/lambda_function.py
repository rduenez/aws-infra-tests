"""
SQS Consumer Lambda using SQLAlchemy ORM.

This Lambda is NOT connected to any event source mapping.
It serves as an alternative ORM-based implementation that can be
manually invoked or connected to events if needed.
"""
import json
import os
from decimal import Decimal
from typing import Optional

from sqlalchemy import create_engine, DECIMAL, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker


# =============================================================================
# SQLAlchemy ORM Models
# =============================================================================

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class ItemModel(Base):
    """SQLAlchemy ORM model for items table."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}')>"


# =============================================================================
# Database Connection
# =============================================================================

def get_database_url() -> str:
    """Build database URL from environment variables."""
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    user = os.environ.get("DB_USER", "admin")
    password = os.environ.get("DB_PASSWORD", "")
    database = os.environ.get("DB_NAME", "cruddb")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def get_session_factory() -> sessionmaker:
    """Create and return a session factory."""
    engine = create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    return sessionmaker(bind=engine, expire_on_commit=False)


# =============================================================================
# Repository
# =============================================================================

class ItemRepository:
    """ORM-based Item repository for Lambda."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, data: dict) -> int:
        """Create a new item and return its ID."""
        item = ItemModel(
            name=data.get("name"),
            description=data.get("description"),
            price=Decimal(str(data["price"])) if data.get("price") is not None else None,
            quantity=data.get("quantity", 0),
        )
        self._session.add(item)
        self._session.commit()
        self._session.refresh(item)
        return item.id


# =============================================================================
# Lambda Handler
# =============================================================================

# Cache session factory for warm starts
_session_factory: Optional[sessionmaker] = None


def get_cached_session_factory() -> sessionmaker:
    """Get or create cached session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = get_session_factory()
    return _session_factory


def lambda_handler(event, context):
    """
    SQS Consumer using SQLAlchemy ORM.

    NOTE: This Lambda is NOT connected to any SQS event source mapping.
    It can be manually invoked or connected later if needed.

    Processes messages from SQS queue and writes to database using ORM.
    """
    processed = 0
    failed = 0
    results = []

    session_factory = get_cached_session_factory()

    for record in event.get("Records", []):
        message_id = record.get("messageId", "unknown")

        try:
            # Parse message body
            message = json.loads(record["body"])
            data = message.get("data", {})

            if not data or not data.get("name"):
                print(f"Skipping message {message_id}: missing required data")
                failed += 1
                continue

            # Use ORM repository to create item
            with session_factory() as session:
                repository = ItemRepository(session)
                inserted_id = repository.create(data)

            print(f"Successfully inserted record with ID: {inserted_id} (message: {message_id})")
            processed += 1
            results.append({
                "messageId": message_id,
                "status": "success",
                "insertedId": inserted_id,
            })

        except Exception as e:
            print(f"Error processing message {message_id}: {str(e)}")
            failed += 1
            results.append({
                "messageId": message_id,
                "status": "error",
                "error": str(e),
            })
            # Re-raise to trigger retry/DLQ
            raise

    return {
        "statusCode": 200,
        "body": json.dumps({
            "processed": processed,
            "failed": failed,
            "results": results,
        }),
    }
