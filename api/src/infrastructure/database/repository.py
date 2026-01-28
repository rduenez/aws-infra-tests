"""
SQLAlchemy ORM Item Repository.
"""
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.database.models import ItemModel


class ItemRepository:
    """
    Repository for Item CRUD operations using SQLAlchemy ORM.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        price: Optional[float] = None,
        quantity: int = 0,
    ) -> ItemModel:
        """
        Create a new item.

        Args:
            name: Item name.
            description: Item description.
            price: Item price.
            quantity: Item quantity.

        Returns:
            The created ItemModel instance.
        """
        async with self._session_factory() as session:
            item = ItemModel(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
            )
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item

    async def get_by_id(self, item_id: int) -> Optional[ItemModel]:
        """
        Get an item by its ID.

        Args:
            item_id: The item ID.

        Returns:
            The ItemModel if found, None otherwise.
        """
        async with self._session_factory() as session:
            stmt = select(ItemModel).where(ItemModel.id == item_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100) -> list[ItemModel]:
        """
        Get all items.

        Args:
            limit: Maximum number of items to return.

        Returns:
            List of ItemModel instances.
        """
        async with self._session_factory() as session:
            stmt = select(ItemModel).order_by(ItemModel.id.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update(self, item_id: int, **kwargs) -> int:
        """
        Update an item.

        Args:
            item_id: The item ID.
            **kwargs: Fields to update (name, description, price, quantity).

        Returns:
            Number of affected rows.
        """
        # Filter out None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            return 0

        async with self._session_factory() as session:
            stmt = (
                update(ItemModel)
                .where(ItemModel.id == item_id)
                .values(**update_data)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def delete(self, item_id: int) -> int:
        """
        Delete an item.

        Args:
            item_id: The item ID.

        Returns:
            Number of affected rows.
        """
        async with self._session_factory() as session:
            stmt = delete(ItemModel).where(ItemModel.id == item_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
