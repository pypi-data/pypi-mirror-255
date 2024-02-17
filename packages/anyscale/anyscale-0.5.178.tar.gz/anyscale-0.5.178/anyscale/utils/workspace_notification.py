import logging

from typing_extensions import Literal


logger = logging.getLogger(__name__)
from anyscale.anyscale_pydantic import BaseModel


class WorkspaceNotificationAction(BaseModel):
    type: Literal["navigate-service", "navigate-workspace-tab", "navigate-external-url"]
    title: str
    value: str


class WorkspaceNotification(BaseModel):
    body: str
    action: WorkspaceNotificationAction


def send_workspace_notification(notification: WorkspaceNotification):
    try:
        import requests

        requests.post(
            "http://localhost:8266/simplefileserver/notifications",
            json=notification.dict(),
        )
    except Exception:
        logger.exception("Failed to send notification to UI")
