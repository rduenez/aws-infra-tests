"""
SQLAlchemy ORM models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
