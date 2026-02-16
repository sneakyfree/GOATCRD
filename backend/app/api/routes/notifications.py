"""
GOATCRD Notifications API Routes
Consumer notification center endpoints
"""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DBSession


router = APIRouter(prefix="/notifications", tags=["notifications"])


# --- In-memory store (replaced by DB in production) ---

_notifications: list[dict] = []


class NotificationResponse(BaseModel):
    """Notification item response."""

    id: str
    type: str  # pulse_alert, system, consent, review, agent
    title: str
    message: str
    is_read: bool
    created_at: str
    metadata: dict = {}


class NotificationsListResponse(BaseModel):
    """List of notifications with metadata."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class CreateNotificationRequest(BaseModel):
    """Internal request to create a notification."""

    consumer_id: str
    type: str = "system"
    title: str
    message: str
    metadata: dict = {}


# --- Helper ---


def _get_user_notifications(user_id: UUID) -> list[dict]:
    """Get notifications for a specific user."""
    return [n for n in _notifications if n["consumer_id"] == str(user_id)]


# --- Endpoints ---


@router.get("", response_model=NotificationsListResponse)
async def list_notifications(
    current_user: CurrentUser,
    db: DBSession,
    unread: bool | None = None,
    type_filter: str | None = Query(None, alias="type"),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> NotificationsListResponse:
    """
    List notifications for the current consumer.

    Supports filtering by read/unread status and notification type.
    """
    user_notifs = _get_user_notifications(current_user.id)

    # Apply filters
    if unread is True:
        user_notifs = [n for n in user_notifs if not n["is_read"]]
    elif unread is False:
        user_notifs = [n for n in user_notifs if n["is_read"]]

    if type_filter:
        user_notifs = [n for n in user_notifs if n["type"] == type_filter]

    # Sort by created_at descending
    user_notifs.sort(key=lambda n: n["created_at"], reverse=True)

    total = len(user_notifs)
    unread_count = sum(1 for n in _get_user_notifications(current_user.id) if not n["is_read"])

    # Paginate
    page = user_notifs[offset : offset + limit]

    return NotificationsListResponse(
        notifications=[
            NotificationResponse(
                id=n["id"],
                type=n["type"],
                title=n["title"],
                message=n["message"],
                is_read=n["is_read"],
                created_at=n["created_at"],
                metadata=n.get("metadata", {}),
            )
            for n in page
        ],
        total=total,
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Mark a single notification as read."""
    for n in _notifications:
        if n["id"] == notification_id and n["consumer_id"] == str(current_user.id):
            n["is_read"] = True
            return {"success": True, "id": notification_id}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notification not found",
    )


@router.post("/read-all")
async def mark_all_read(
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Mark all notifications as read for the current user."""
    count = 0
    for n in _notifications:
        if n["consumer_id"] == str(current_user.id) and not n["is_read"]:
            n["is_read"] = True
            count += 1

    return {"success": True, "marked_count": count}


@router.post("/create")
async def create_notification(
    request: CreateNotificationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> NotificationResponse:
    """
    Create a notification (internal use).

    In production, notifications are created by services/engines,
    not directly by consumers. This endpoint exists for testing
    and admin use.
    """
    notif = {
        "id": str(uuid4()),
        "consumer_id": request.consumer_id,
        "type": request.type,
        "title": request.title,
        "message": request.message,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": request.metadata,
    }
    _notifications.append(notif)

    return NotificationResponse(
        id=notif["id"],
        type=notif["type"],
        title=notif["title"],
        message=notif["message"],
        is_read=notif["is_read"],
        created_at=notif["created_at"],
        metadata=notif["metadata"],
    )
