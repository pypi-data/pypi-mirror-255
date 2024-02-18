#  Copyright (c) 2023 Roboto Technologies, Inc.

import abc
from typing import Optional

from roboto.notifications import (
    NotificationChannel,
    NotificationType,
)

from .user_record import UserRecord


class UserDelegate(abc.ABC):
    @abc.abstractmethod
    def get_user_by_id(self, user_id: Optional[str] = None) -> UserRecord:
        raise NotImplementedError("get_user_by_id")

    @abc.abstractmethod
    def delete_user(self, user_id: Optional[str] = None) -> None:
        raise NotImplementedError("delete_user")

    @abc.abstractmethod
    def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        picture_url: Optional[str] = None,
        notification_channels_enabled: Optional[dict[NotificationChannel, bool]] = None,
        notification_types_enabled: Optional[dict[NotificationType, bool]] = None,
    ) -> UserRecord:
        raise NotImplementedError("update_user")
