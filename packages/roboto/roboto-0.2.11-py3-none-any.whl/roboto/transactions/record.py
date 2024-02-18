import datetime
import enum
import typing

import pydantic


class TransactionType(str, enum.Enum):
    FileUpload = "file_upload"


class TransactionStatus(str, enum.Enum):
    Pending = "pending"
    Completed = "completed"


class TransactionRecordV1(pydantic.BaseModel):
    """
    This is the model that is returned by the v1 API.
    It is deprecated and should not be used.
    Use TransactionRecord instead.
    """

    org_id: str
    transaction_id: str
    transaction_type: TransactionType
    transaction_status: TransactionStatus  # This field is deprecated
    origination: str
    resource_count: int = 0
    expected_resource_count: typing.Optional[int] = None
    created: datetime.datetime
    created_by: str
    modified: datetime.datetime
    modified_by: str = "This field is deprecated"


class TransactionRecord(pydantic.BaseModel):
    org_id: str
    transaction_id: str
    transaction_type: TransactionType
    origination: str
    expected_resource_count: typing.Optional[int] = None
    created: datetime.datetime
    created_by: str
    modified: datetime.datetime
