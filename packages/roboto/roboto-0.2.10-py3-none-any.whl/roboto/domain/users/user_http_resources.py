#  Copyright (c) 2023 Roboto Technologies, Inc.
from typing import Optional

import pydantic

from roboto.notifications import (
    NotificationChannel,
    NotificationType,
)


class UpdateUserRequest(pydantic.BaseModel):
    name: Optional[str] = None
    picture_url: Optional[str] = None
    notification_channels_enabled: Optional[dict[NotificationChannel, bool]] = None
    notification_types_enabled: Optional[dict[NotificationType, bool]] = None
