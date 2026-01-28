from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Request DTOs
# =============================================================================

class CreateItemRequest(BaseModel):
    """Request DTO for creating an item."""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, max_length=5000, description="Item description")
    price: Optional[float] = Field(None, ge=0, description="Item price")
    quantity: int = Field(default=0, ge=0, description="Item quantity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Widget",
                "description": "A useful widget",
                "price": 29.99,
                "quantity": 100
            }
        }
    )


class UpdateItemRequest(BaseModel):
    """Request DTO for updating an item."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, max_length=5000, description="Item description")
    price: Optional[float] = Field(None, ge=0, description="Item price")
    quantity: Optional[int] = Field(None, ge=0, description="Item quantity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Widget",
                "price": 39.99
            }
        }
    )


class QueueItemRequest(BaseModel):
    """Request DTO for queueing an item creation."""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, max_length=5000, description="Item description")
    price: Optional[float] = Field(None, ge=0, description="Item price")
    quantity: int = Field(default=0, ge=0, description="Item quantity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Async Widget",
                "description": "Created via SQS",
                "price": 19.99,
                "quantity": 50
            }
        }
    )


# =============================================================================
# Response DTOs
# =============================================================================

class ItemResponse(BaseModel):
    """Response DTO for a single item."""

    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Response DTO for a list of items."""

    data: list[ItemResponse]
    count: int


class CreateItemResponse(BaseModel):
    """Response DTO for item creation."""

    message: str = "Item created successfully"
    id: int


class UpdateItemResponse(BaseModel):
    """Response DTO for item update."""

    message: str = "Item updated successfully"
    affected_rows: int


class DeleteItemResponse(BaseModel):
    """Response DTO for item deletion."""

    message: str = "Item deleted successfully"
    affected_rows: int


class QueueItemResponse(BaseModel):
    """Response DTO for queued item creation."""

    message: str = "Item creation queued successfully"
    message_id: str
