import collections.abc
import typing
import urllib.parse

from ...association import Association
from ...exceptions import RobotoHttpExceptionParse
from ...http import (
    HttpClient,
    PaginatedList,
    roboto_headers,
)
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

CONTENT_TYPE_JSON = {"Content-Type": "application/json"}


class TopicHttpDelegate(TopicDelegate):
    __http_client: HttpClient
    __roboto_service_base_url: str

    def __init__(self, roboto_service_base_url: str, http_client: HttpClient):
        self.__http_client = http_client
        self.__roboto_service_base_url = roboto_service_base_url

    def add_message_path(
        self, topic_record: TopicRecord, request: AddMessagePathRequest
    ) -> MessagePathRecord:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
                "message-path",
            ]
        )
        with RobotoHttpExceptionParse():
            response = self.__http_client.post(
                url,
                data=request.model_dump_json(),
                headers=roboto_headers(
                    resource_owner_id=topic_record.org_id,
                    additional_headers=CONTENT_TYPE_JSON,
                ),
            )

        return MessagePathRecord.model_validate(response.from_json(json_path=["data"]))

    def add_message_path_representation(
        self, topic_record: TopicRecord, request: AddMessagePathRepresentationRequest
    ) -> RepresentationRecord:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
                "message-path/representation",
            ]
        )
        with RobotoHttpExceptionParse():
            response = self.__http_client.post(
                url,
                data=request.model_dump_json(),
                headers=roboto_headers(
                    resource_owner_id=topic_record.org_id,
                    additional_headers=CONTENT_TYPE_JSON,
                ),
            )

        return RepresentationRecord.model_validate(
            response.from_json(json_path=["data"])
        )

    def create_topic(self, request: CreateTopicRequest) -> TopicRecord:
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
            ]
        )

        with RobotoHttpExceptionParse():
            response = self.__http_client.post(
                url,
                data=request.model_dump_json(exclude_none=True),
                headers=roboto_headers(
                    resource_owner_id=request.org_id,
                    additional_headers=CONTENT_TYPE_JSON,
                ),
            )
        return TopicRecord.model_validate(response.from_json(json_path=["data"]))

    def get_message_paths(
        self, topic_record: TopicRecord
    ) -> collections.abc.Sequence[MessagePathRecord]:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}/message-path",
            ]
        )

        with RobotoHttpExceptionParse():
            response = self.__http_client.get(
                url,
                headers=roboto_headers(resource_owner_id=topic_record.org_id),
            )
        return [
            MessagePathRecord.model_validate(record)
            for record in response.from_json(json_path=["data"])
        ]

    def get_topic_by_name_and_association(
        self,
        topic_name: str,
        association: Association,
        org_id: typing.Optional[str] = None,
    ) -> TopicRecord:
        quoted_topic_name = urllib.parse.quote_plus(topic_name)
        encoded_association = association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
            ]
        )

        with RobotoHttpExceptionParse():
            response = self.__http_client.get(
                url,
                headers=roboto_headers(resource_owner_id=org_id),
            )
        return TopicRecord.model_validate(response.from_json(json_path=["data"]))

    def get_topics_by_association(
        self,
        association: Association,
        org_id: typing.Optional[str] = None,
        page_token: typing.Optional[str] = None,
    ) -> PaginatedList[TopicRecord]:
        encoded_association = association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}",
            ]
        )
        if page_token:
            url = f"{url}?page_token={page_token}"

        with RobotoHttpExceptionParse():
            response = self.__http_client.get(
                url,
                headers=roboto_headers(resource_owner_id=org_id),
            )

        unmarshalled = response.from_json(json_path=["data"])
        return PaginatedList(
            items=[
                TopicRecord.model_validate(topic_record)
                for topic_record in unmarshalled["items"]
            ],
            next_token=unmarshalled["next_token"],
        )

    def hard_delete_topic(
        self,
        topic_record: TopicRecord,
    ) -> None:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}/hard",
            ]
        )
        with RobotoHttpExceptionParse():
            self.__http_client.delete(
                url,
                headers=roboto_headers(resource_owner_id=topic_record.org_id),
            )

    def set_default_representation(
        self, topic_record: TopicRecord, request: SetDefaultRepresentationRequest
    ) -> RepresentationRecord:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
                "representation",
            ]
        )
        with RobotoHttpExceptionParse():
            response = self.__http_client.post(
                url,
                data=request.model_dump_json(),
                headers=roboto_headers(
                    resource_owner_id=topic_record.org_id,
                    additional_headers=CONTENT_TYPE_JSON,
                ),
            )

        return RepresentationRecord.model_validate(
            response.from_json(json_path=["data"])
        )

    def soft_delete_topic(
        self,
        topic_record: TopicRecord,
    ) -> None:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
            ]
        )
        with RobotoHttpExceptionParse():
            self.__http_client.delete(
                url,
                headers=roboto_headers(resource_owner_id=topic_record.org_id),
            )

    def update_topic(
        self, topic_record: TopicRecord, request: UpdateTopicRequest
    ) -> TopicRecord:
        quoted_topic_name = urllib.parse.quote_plus(topic_record.topic_name)
        encoded_association = topic_record.association.url_encode()
        url = "/".join(
            [
                self.__roboto_service_base_url,
                "v1/topics",
                f"association/{encoded_association}/name/{quoted_topic_name}",
            ]
        )

        with RobotoHttpExceptionParse():
            response = self.__http_client.put(
                url,
                data=request.model_dump_json(
                    exclude_none=True, exclude_unset=True, exclude_defaults=True
                ),
                headers=roboto_headers(
                    resource_owner_id=topic_record.org_id,
                    additional_headers=CONTENT_TYPE_JSON,
                ),
            )
        return TopicRecord.model_validate(response.from_json(json_path=["data"]))
