import typing

import pydantic

from .record import TransactionType


class BeginTransactionRequest(pydantic.BaseModel):
    transaction_type: TransactionType
    origination: str
    expected_resource_count: typing.Optional[int] = None


class TransactionCompletionResponse(pydantic.BaseModel):
    is_complete: bool
