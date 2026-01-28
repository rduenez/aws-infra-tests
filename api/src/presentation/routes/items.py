"""
Items CRUD routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dto import (
    CreateItemRequest,
    CreateItemResponse,
    DeleteItemResponse,
    ItemListResponse,
    ItemResponse,
    UpdateItemRequest,
    UpdateItemResponse,
)
from src.presentation.dependencies import Container, get_container

router = APIRouter(prefix="/items", tags=["Items"])


@router.post(
    "",
    response_model=CreateItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Creates a new item in the database with the provided data.",
)
async def create_item(
    request: CreateItemRequest,
    container: Container = Depends(get_container),
):
    """Create a new item."""
    item = await container.item_service.create_item(
        name=request.name,
        description=request.description,
        price=request.price,
        quantity=request.quantity,
    )
    return CreateItemResponse(id=item.id)


@router.get(
    "",
    response_model=ItemListResponse,
    summary="List all items",
    description="Retrieves a list of all items with optional limit.",
)
async def list_items(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of items to return"),
    container: Container = Depends(get_container),
):
    """List all items."""
    items = await container.item_service.get_all_items(limit=limit)
    return ItemListResponse(
        data=[ItemResponse.model_validate(item) for item in items],
        count=len(items),
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    description="Retrieves a single item by its unique identifier.",
)
async def get_item(
    item_id: int,
    container: Container = Depends(get_container),
):
    """Get an item by ID."""
    item = await container.item_service.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return ItemResponse.model_validate(item)


@router.put(
    "/{item_id}",
    response_model=UpdateItemResponse,
    summary="Update an item",
    description="Updates an existing item with the provided data.",
)
async def update_item(
    item_id: int,
    request: UpdateItemRequest,
    container: Container = Depends(get_container),
):
    """Update an item."""
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    affected_rows = await container.item_service.update_item(item_id, **update_data)

    if affected_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )

    return UpdateItemResponse(affected_rows=affected_rows)


@router.delete(
    "/{item_id}",
    response_model=DeleteItemResponse,
    summary="Delete an item",
    description="Deletes an item by its unique identifier.",
)
async def delete_item(
    item_id: int,
    container: Container = Depends(get_container),
):
    """Delete an item."""
    affected_rows = await container.item_service.delete_item(item_id)

    if affected_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )

    return DeleteItemResponse(affected_rows=affected_rows)
