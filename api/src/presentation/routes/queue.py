from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dto import QueueItemRequest, QueueItemResponse
from src.presentation.dependencies import Container, get_container

router = APIRouter(prefix="/queue", tags=["Queue"])


@router.post(
    "",
    response_model=QueueItemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue item creation",
    description="Sends an item creation request to the SQS queue for asynchronous processing.",
)
async def queue_item_creation(
    request: QueueItemRequest,
    container: Container = Depends(get_container),
):
    """Queue an item creation request for async processing."""
    if not container.settings.sqs_queue_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SQS queue URL not configured",
        )

    message = {
        "operation": "create",
        "table": "items",
        "data": {
            "name": request.name,
            "description": request.description,
            "price": request.price,
            "quantity": request.quantity,
        },
    }

    try:
        message_id = await container.message_queue.send_message(message)
        return QueueItemResponse(message_id=message_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue message: {str(e)}",
        )
