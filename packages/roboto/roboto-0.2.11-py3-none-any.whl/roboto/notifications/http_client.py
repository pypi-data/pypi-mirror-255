#  Copyright (c) 2023 Roboto Technologies, Inc.

from typing import Any, Optional

from roboto.exceptions import (
    RobotoHttpExceptionParse,
)
from roboto.http import HttpClient

from .notifications import NotificationChannel


class NotificationsClient:
    __http_client: HttpClient

    def __init__(self, http_client: HttpClient):
        super().__init__()
        self.__http_client = http_client

    def get_notifications(self) -> dict[str, Any]:
        url = self.__http_client.url("v1/notifications")

        with RobotoHttpExceptionParse():
            response = self.__http_client.get(url=url)

            return response.from_json(json_path=["data"])

    def update_notification(
        self,
        notification_id: str,
        org_id: Optional[str] = None,
        read_status: Optional[str] = None,
        lifecycle_status: Optional[dict[NotificationChannel, str]] = None,
    ) -> Any:
        url = self.__http_client.url(f"v1/notifications/{notification_id}")

        body: dict[str, Any] = {}

        request_headers: Optional[dict[str, str]] = None

        if org_id is not None:
            request_headers = {
                "X-Roboto-Org-Id": org_id,
            }

        if read_status is not None:
            body["read_status"] = read_status

        if lifecycle_status is not None:
            body["lifecycle_status"] = lifecycle_status

        with RobotoHttpExceptionParse():
            response = self.__http_client.put(
                url=url,
                data=body,
                headers=request_headers,
            )

            return response.from_json(json_path=["data"])

    def delete_notification(self, notification_id: str) -> None:
        url = self.__http_client.url(f"v1/notifications/{notification_id}")

        with RobotoHttpExceptionParse():
            self.__http_client.delete(
                url=url,
            )

            return None
