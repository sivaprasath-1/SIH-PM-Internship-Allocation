from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notif_type: str = "info",
):
    """Create a notification for a user."""
    type_map = {
        "info": NotificationType.INFO,
        "success": NotificationType.SUCCESS,
        "warning": NotificationType.WARNING,
        "error": NotificationType.ERROR,
        "application": NotificationType.APPLICATION,
        "allocation": NotificationType.ALLOCATION,
        "recommendation": NotificationType.RECOMMENDATION,
    }

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type_map.get(notif_type, NotificationType.INFO),
    )
    db.add(notification)
    db.commit()
    return notification
