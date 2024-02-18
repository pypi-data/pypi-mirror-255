import base64
import enum
import json
import typing

import pydantic

from roboto.exceptions import (
    RobotoDomainException,
)

from ..logging import default_logger

logger = default_logger()

Model = typing.TypeVar("Model")


class BatchRequest(pydantic.BaseModel, typing.Generic[Model]):
    requests: list[Model]


class BatchResponseElement(pydantic.BaseModel, typing.Generic[Model]):
    """
    One element of a response to a batch request. This should only ever have data set (in case of a successful
    operation) or error set (in case of a failed operation). For operations that do not return a response, an empty
    (data = None, error = None) Batch Response Element will be effectively equivalent to a single requests 204 No
    Content
    """

    data: typing.Optional[Model] = None
    error: typing.Optional[RobotoDomainException] = None

    @pydantic.field_validator("error", mode="before")
    def validate_error(cls, value: str) -> typing.Optional[RobotoDomainException]:
        try:
            return RobotoDomainException.from_json(json.loads(value))
        except Exception:
            return None

    @pydantic.field_serializer("error")
    def serialize_error(
        self,
        value: typing.Optional[RobotoDomainException],
        info: pydantic.SerializationInfo,
    ) -> typing.Optional[dict[str, typing.Any]]:
        return None if value is None else value.to_dict()


class BatchResponse(pydantic.BaseModel, typing.Generic[Model]):
    """
    The response to a batch request. The responses element contains one response (either success data or failure error)
    per request element, in the order in which the request was sent.
    """

    responses: list[BatchResponseElement[Model]]


class PaginatedList(pydantic.BaseModel, typing.Generic[Model]):
    """
    A list of records pulled from a paginated result set.
    It may be a subset of that result set,
    in which case `next_token` will be set and can be used to fetch the next page.
    """

    items: list[Model]
    # Opaque token that can be used to fetch the next page of results.
    next_token: typing.Optional[str] = None


class StreamedList(pydantic.BaseModel, typing.Generic[Model]):
    """
    A StreamedList differs from a PaginatedList in that it represents a stream of data that is
    in process of being written to. Unlike a result set, which is finite and complete,
    a stream may be infinite, and it is unknown when or if it will complete.
    """

    items: list[Model]
    # Opaque token that can be used to fetch the next page of results.
    last_read: typing.Optional[str]
    # If True, it is known that there are more items to be fetched;
    # use `last_read` as a pagination token to fetch those additional records.
    # If False, it is not known if there are more items to be fetched.
    has_next: bool


class PaginationTokenEncoding(enum.Enum):
    Json = "json"
    Raw = "raw"


class PaginationTokenScheme(enum.Enum):
    V1 = "v1"


class PaginationToken:
    """
    A pagination token that can be treated as a truly opaque token by clients,
    with support for evolving the token format over time.
    """

    __scheme: PaginationTokenScheme
    __encoding: PaginationTokenEncoding
    __data: typing.Any

    @staticmethod
    def empty() -> "PaginationToken":
        return PaginationToken(
            PaginationTokenScheme.V1, PaginationTokenEncoding.Raw, None
        )

    @staticmethod
    def encode(data: str) -> str:
        """Base64 encode the data and strip all trailing padding ("=")."""
        return (
            base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8").rstrip("=")
        )

    @staticmethod
    def decode(data: str) -> str:
        """Base64 decode the data, adding back any trailing padding ("=") as necessary to make data properly Base64."""
        while len(data) % 4 != 0:
            data += "="
        return base64.urlsafe_b64decode(data).decode("utf-8")

    @classmethod
    def from_token(cls, token: typing.Optional[str]) -> "PaginationToken":
        if token is None:
            return PaginationToken.empty()
        try:
            decoded = PaginationToken.decode(token)
            if not decoded.startswith(PaginationTokenScheme.V1.value):
                logger.error("Invalid pagination token scheme %s", decoded)
                raise ValueError("Invalid pagination token scheme")
            scheme, encoding, data = decoded.split(":", maxsplit=2)
            pagination_token_scheme = PaginationTokenScheme(scheme)
            pagination_token_encoding = PaginationTokenEncoding(encoding)
            return cls(
                pagination_token_scheme,
                pagination_token_encoding,
                json.loads(data)
                if pagination_token_encoding == PaginationTokenEncoding.Json
                else data,
            )
        except Exception as e:
            logger.error(f"Invalid pagination token {token}", exc_info=e)
            raise ValueError("Invalid pagination token format") from None

    def __init__(
        self,
        scheme: PaginationTokenScheme,
        encoding: PaginationTokenEncoding,
        data: typing.Any,
    ):
        self.__scheme = scheme
        self.__encoding = encoding
        self.__data = data

    def __len__(self):
        return len(str(self)) if self.__data else 0

    def __str__(self):
        return self.to_token()

    @property
    def data(self) -> typing.Any:
        return self.__data

    def to_token(self) -> str:
        data = (
            json.dumps(self.__data)
            if self.__encoding == PaginationTokenEncoding.Json
            else self.__data
        )
        return PaginationToken.encode(
            f"{self.__scheme.value}:{self.__encoding.value}:{data}"
        )
