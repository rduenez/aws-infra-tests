"""
Item domain service.
"""
from typing import Optional

from src.infrastructure.database import ItemRepository, ItemModel


class ItemService:
    """Service for Item business logic."""

    def __init__(self, repository: ItemRepository):
        self._repository = repository

    async def create_item(
        self,
        name: str,
        description: Optional[str] = None,
        price: Optional[float] = None,
        quantity: int = 0,
    ) -> ItemModel:
        """Create a new item."""
        return await self._repository.create(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
        )

    async def get_item(self, item_id: int) -> Optional[ItemModel]:
        """Get an item by ID."""
        return await self._repository.get_by_id(item_id)

    async def get_all_items(self, limit: int = 100) -> list[ItemModel]:
        """Get all items."""
        return await self._repository.get_all(limit=limit)

    async def update_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        quantity: Optional[int] = None,
    ) -> int:
        """Update an item."""
        return await self._repository.update(
            item_id,
            name=name,
            description=description,
            price=price,
            quantity=quantity,
        )

    async def delete_item(self, item_id: int) -> int:
        """Delete an item."""
        return await self._repository.delete(item_id)
