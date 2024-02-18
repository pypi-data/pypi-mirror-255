import collections.abc
import typing

import pydantic

from ...association import Association
from ...sentinels import NotSet, NotSetType
from ...updates import MetadataChangeset
from .topic_record import (
    CanonicalDataType,
    RepresentationContext,
    RepresentationStorageFormat,
)


class BaseAddRepresentationRequest(pydantic.BaseModel):
    association: Association
    storage_format: RepresentationStorageFormat
    context: typing.Optional[RepresentationContext] = None
    version: int
    org_id: str


class SetDefaultRepresentationRequest(BaseAddRepresentationRequest):
    """Memorialize a representation of topic data contained within a source recording file."""

    model_config = pydantic.ConfigDict(extra="forbid")


class AddMessagePathRepresentationRequest(BaseAddRepresentationRequest):
    """Associate a MessagePath with a Representation."""

    topic_message_path_id: int

    model_config = pydantic.ConfigDict(extra="forbid")


class AddMessagePathRequest(pydantic.BaseModel):
    """Associate a MessagePath with a Topic."""

    message_path: str
    data_type: str
    canonical_data_type: CanonicalDataType

    model_config = pydantic.ConfigDict(extra="forbid")


class CreateTopicRequest(pydantic.BaseModel):
    """Memorialize a topic contained within a source recording file."""

    # Required
    association: Association
    topic_name: str
    org_id: str

    # Optional
    end_time: typing.Optional[int] = None
    message_count: typing.Optional[int] = None
    metadata: typing.Optional[collections.abc.Mapping[str, typing.Any]] = None
    schema_checksum: typing.Optional[str] = None
    schema_name: typing.Optional[str] = None
    start_time: typing.Optional[int] = None

    model_config = pydantic.ConfigDict(extra="forbid")


class UpdateTopicRequest(pydantic.BaseModel):
    """Update a Topic."""

    end_time: typing.Union[typing.Optional[int], NotSetType] = NotSet
    message_count: typing.Union[int, NotSetType] = NotSet
    schema_checksum: typing.Union[typing.Optional[str], NotSetType] = NotSet
    schema_name: typing.Union[typing.Optional[str], NotSetType] = NotSet
    start_time: typing.Union[typing.Optional[int], NotSetType] = NotSet
    metadata_changeset: typing.Union[MetadataChangeset, NotSetType] = NotSet

    model_config = pydantic.ConfigDict(
        extra="forbid", json_schema_extra=NotSetType.openapi_schema_modifier
    )
