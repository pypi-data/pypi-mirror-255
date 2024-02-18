import collections.abc
import datetime
import enum
import typing

import pydantic

from ...association import Association
from ...exceptions import RobotoInternalException


class RepresentationStorageFormat(enum.Enum):
    MCAP = "mcap"


class RepresentationContext(pydantic.BaseModel):
    """
    Base class for typed, contextual metadata helpful for representing data in a particular modality.
    """

    subclasses: typing.ClassVar[list[type]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @classmethod
    def from_mapping(
        cls, data: typing.Optional[collections.abc.Mapping[str, typing.Any]]
    ) -> typing.Optional["RepresentationContext"]:
        if data is None:
            return None

        for subclass in cls.subclasses:
            try:
                return subclass(data)
            except pydantic.ValidationError:
                pass
        raise RobotoInternalException(
            f"Could not parse RepresentationContext from dict: {data}"
        )


class TimeseriesPlotContext(RepresentationContext):
    extents: dict[str, tuple[float, float]]
    """
    [min, max] for each dimension of the data.
    Dictionary keys are message paths in dot notation (e.g., "pose.position.x").
    """


class RepresentationRecord(pydantic.BaseModel):
    """
    Pointer to data extracted from a Topic--potentially a specific slice of the data,
    from within a MessagePath--processed for representation in a particular modality,
    optionally with contextual metadata helpful for working with that representation.

    Most MessagePaths within a Topic will point to the same Representation
    (e.g., an MCAP file with all of the Topic data).
    Some MessagePaths, however, may have more than one Representation,
    such as both an MCAP and a preview GIF or statically rendered, line-chart preview.
    """

    association: Association
    """
    Identifier and entity type with which this Representation is associated. E.g., a file, a database.
    """

    context: typing.Optional[RepresentationContext] = None

    representation_id: int
    """Internal identifier for this Representation."""

    storage_format: RepresentationStorageFormat
    topic_id: int
    version: int


class CanonicalDataType(enum.Enum):
    """
    Well-known (and simplified) data types, normalized across frameworks/technologies.
    Primarily used for UI purposes to determine if a Panel can render a particular MessagePath.

    References:
        - ROS1 field types: http://wiki.ros.org/msg
        - ROS2 field types: https://docs.ros.org/en/iron/Concepts/Basic/About-Interfaces.html#field-types
        - uORB: there is no canonical list of primitive field types, but they appear to be the same as ROS.
            The documentation states:
            > Have a look at the existing msg files for supported types.
            > A message can also be used nested in other messages.
            From https://docs.px4.io/main/en/middleware/uorb.html#adding-a-new-topic

    Example mappings:
    - "float32" -> DataType.Number
    - "uint8[]" -> DataType.Array
    - "geometry_msgs/Pose" -> DataType.Object
    - "std_msgs/Header" -> DataType.Object
    - "string" -> DataType.String
    - "char" -> DataType.String
    - "bool" -> DataType.Boolean
    - "byte" -> DataType.Byte

    """

    Array = "array"  # A sequence of values.
    Boolean = "boolean"
    Byte = "byte"
    Number = "number"
    Object = "object"  # A struct with attributes.
    String = "string"
    Unknown = "unknown"  # This is a fallback and should be used sparingly.


class MessagePathRecord(pydantic.BaseModel):
    """
    Path to a typed attribute within individual datum records contained within a Topic.
    """

    message_path: str
    """
    Dot-delimited path to the attribute within the datum record.
    """

    data_type: str
    """
    'Native'/framework-specific data type of the attribute at this path.
    E.g. "float32", "unint8[]", "geometry_msgs/Pose", "string".
    """

    canonical_data_type: CanonicalDataType

    representations: list[RepresentationRecord] = pydantic.Field(default_factory=list)
    """
    Zero to many Representations of this MessagePath.
    """

    topic_message_path_id: int
    """Internal identifier for this MessagePath, joined to a particular Topic."""


class TopicRecord(pydantic.BaseModel):
    """
    Collection of timestamped data that share a common name and association (e.g., file).

    Data from the same file within the same named topic/channel are considered part of the same Topic.
    Data from different files or with differently named topics/channels belong within unique Topics.

    Source files that have been chunked by time or size but from the same point-in-time data collection will
    produce multiple Topics for the same "logical topic" (~= name, schema) within those chunks.
    """

    association: Association
    """
    Identifier and entity type with which this Topic is associated. E.g., a file, a dataset.
    """

    created: datetime.datetime

    default_representation: typing.Optional[RepresentationRecord] = None
    """
    Default Representation for this Topic.
    Assume that if a MessagePath is not more specifically associated with a Representation,
    it should use this one.
    """

    end_time: typing.Optional[int] = None
    """
    Timestamp of oldest message in topic, in nanoseconds since epoch (assumed Unix epoch).
    """

    message_count: typing.Optional[int] = None

    message_paths: list[MessagePathRecord] = pydantic.Field(default_factory=list)
    """
    Zero to many MessagePathRecords associated with this TopicSource.
    """

    metadata: collections.abc.Mapping[str, typing.Any] = pydantic.Field(
        default_factory=dict
    )
    """
    Arbitrary metadata.
    """

    modified: datetime.datetime

    org_id: str

    schema_checksum: typing.Optional[str] = None
    """
    Checksum of topic schema.
    May be None if topic does not have a known/named schema.
    """

    schema_name: typing.Optional[str] = None
    """
    Type of messages in topic. E.g., "sensor_msgs/PointCloud2".
    May be None if topic does not have a known/named schema.
    """

    schema_version: int = 0
    """
    Dynamically-determined at write-time.
    A more human-friendly way by which to compare schemas than schema_checksum.
    Schemas with the same (name, checksum) ought to have the same version.
    It communicates, "this is the Nth version of a topic with this name that has been uploaded to Roboto".
    """

    start_time: typing.Optional[int] = None
    """
    Timestamp of earliest message in topic, in nanoseconds since epoch (assumed Unix epoch).
    """

    topic_id: int
    topic_name: str
