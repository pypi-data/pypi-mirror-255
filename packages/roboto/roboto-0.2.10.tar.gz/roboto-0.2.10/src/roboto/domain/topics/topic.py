import collections.abc
import typing

from ...association import Association
from .topic_delegate import TopicDelegate
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


class Topic:
    __record: TopicRecord
    __topic_delegate: TopicDelegate

    @classmethod
    def get_by_association(
        cls,
        association: Association,
        topic_delegate: TopicDelegate,
        org_id: typing.Optional[str] = None,
    ) -> collections.abc.Generator["Topic", None, None]:
        paginated_results = topic_delegate.get_topics_by_association(
            association, org_id
        )
        while True:
            for topic_record in paginated_results.items:
                yield cls(topic_record, topic_delegate)
            if paginated_results.next_token:
                paginated_results = topic_delegate.get_topics_by_association(
                    association, org_id, paginated_results.next_token
                )
            else:
                break

    @classmethod
    def create(
        cls,
        request: CreateTopicRequest,
        topic_delegate: TopicDelegate,
    ) -> "Topic":
        topic_record = topic_delegate.create_topic(request)
        return cls(topic_record, topic_delegate)

    @classmethod
    def from_name_and_association(
        cls,
        topic_name: str,
        association: Association,
        topic_delegate: TopicDelegate,
        org_id: typing.Optional[str] = None,
    ) -> "Topic":
        topic_record = topic_delegate.get_topic_by_name_and_association(
            topic_name, association, org_id
        )
        return cls(topic_record, topic_delegate)

    def __init__(
        self,
        record: TopicRecord,
        topic_delegate: TopicDelegate,
    ):
        self.__record = record
        self.__topic_delegate = topic_delegate

    @property
    def message_paths(self) -> collections.abc.Sequence[MessagePathRecord]:
        return self.__record.message_paths

    @property
    def record(self) -> TopicRecord:
        return self.__record

    def set_default_representation(
        self, request: SetDefaultRepresentationRequest
    ) -> RepresentationRecord:
        representation_record = self.__topic_delegate.set_default_representation(
            self.__record, request
        )
        self.__refresh_record()
        return representation_record

    def add_message_path(self, request: AddMessagePathRequest) -> MessagePathRecord:
        message_path_record = self.__topic_delegate.add_message_path(
            self.__record, request
        )
        self.__refresh_record()
        return message_path_record

    def add_message_path_representation(
        self,
        request: AddMessagePathRepresentationRequest,
    ) -> RepresentationRecord:
        representation = self.__topic_delegate.add_message_path_representation(
            self.__record, request
        )
        self.__refresh_record()
        return representation

    def delete(self) -> None:
        self.__topic_delegate.soft_delete_topic(self.__record)

    def update(self, request: UpdateTopicRequest) -> None:
        self.__topic_delegate.update_topic(self.__record, request)

    def __refresh_record(self) -> None:
        self.__record = self.__topic_delegate.get_topic_by_name_and_association(
            self.__record.topic_name, self.__record.association, self.__record.org_id
        )
