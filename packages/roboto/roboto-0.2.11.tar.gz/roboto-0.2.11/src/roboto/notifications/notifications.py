#  Copyright (c) 2023 Roboto Technologies, Inc.

from enum import Enum


class NotificationType(str, Enum):
    CommentMention = "comment_mention"
    # CommentOnThread = "comment_on_thread"
    # CommentOnAuthoredAction = "comment_on_authored_action"
    # etc...


class NotificationChannel(str, Enum):
    Email = "email"
    # Slack = "slack"
    # SMS = "sms"
    # ApplePush = "apple_push"
    # AndroidPush = "android_push"
    # etc...
