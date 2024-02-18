import abc
import collections.abc
import typing

from ...association import Association
from ...http import PaginatedList
from .topic_record import (
    MessagePathRecord,
    RepresentationRecord,
    TopicRecord,
)
from .topic_requests import (
    AddMessagePathRepresentationRequest,
    AddMessagePathRequest,
    CreateTopicRequest,
    SetDefaultRepresentationRequest,
    UpdateTopicRequest,
)


class TopicDelegate(abc.ABC):
    @abc.abstractmethod
    def add_message_path(
        self, topic_record: TopicRecord, request: AddMessagePathRequest
    ) -> MessagePathRecord:
        raise NotImplementedError("add_message_path")

    @abc.abstractmethod
    def add_message_path_representation(
        self, topic_record: TopicRecord, request: AddMessagePathRepresentationRequest
    ) -> RepresentationRecord:
        raise NotImplementedError("add_message_path_representation")

    @abc.abstractmethod
    def create_topic(self, request: CreateTopicRequest) -> TopicRecord:
        raise NotImplementedError("create_topic")

    @abc.abstractmethod
    def get_message_paths(
        self, topic_record: TopicRecord
    ) -> collections.abc.Sequence[MessagePathRecord]:
        raise NotImplementedError("get_message_paths")

    @abc.abstractmethod
    def get_topic_by_name_and_association(
        self,
        topic_name: str,
        association: Association,
        org_id: typing.Optional[str] = None,
    ) -> TopicRecord:
        raise NotImplementedError("get_topic_by_name_and_association")

    @abc.abstractmethod
    def get_topics_by_association(
        self,
        association: Association,
        org_id: typing.Optional[str] = None,
        page_token: typing.Optional[str] = None,
    ) -> PaginatedList[TopicRecord]:
        raise NotImplementedError("get_topics_by_association")

    @abc.abstractmethod
    def hard_delete_topic(
        self,
        topic_record: TopicRecord,
    ) -> None:
        raise NotImplementedError("hard_delete_topic")

    @abc.abstractmethod
    def set_default_representation(
        self, topic_record: TopicRecord, request: SetDefaultRepresentationRequest
    ) -> RepresentationRecord:
        raise NotImplementedError("set_default_representation")

    @abc.abstractmethod
    def soft_delete_topic(
        self,
        topic_record: TopicRecord,
    ) -> None:
        raise NotImplementedError("soft_delete_topic")

    @abc.abstractmethod
    def update_topic(
        self, topic_record: TopicRecord, request: UpdateTopicRequest
    ) -> TopicRecord:
        raise NotImplementedError("update_topic")
