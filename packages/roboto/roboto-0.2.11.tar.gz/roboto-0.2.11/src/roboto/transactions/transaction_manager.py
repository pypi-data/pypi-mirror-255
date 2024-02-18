import typing

from ..exceptions import RobotoHttpExceptionParse
from ..http import HttpClient, roboto_headers
from .http_resources import (
    BeginTransactionRequest,
    TransactionCompletionResponse,
)
from .manager_abc import TransactionManagerABC
from .record import (
    TransactionRecord,
    TransactionType,
)


class TransactionManager(TransactionManagerABC):
    __http_client: HttpClient
    __roboto_service_base_url: str

    def __init__(self, roboto_service_base_url: str, http_client: HttpClient) -> None:
        self.__http_client = http_client
        self.__roboto_service_base_url = roboto_service_base_url

    def begin_transaction(
        self,
        transaction_type: TransactionType,
        origination: str,
        expected_resource_count: typing.Optional[int] = None,
        org_id: typing.Optional[str] = None,
        caller: typing.Optional[str] = None,
        resource_owner_id: typing.Optional[str] = None,
    ) -> TransactionRecord:
        url = f"{self.__roboto_service_base_url}/v2/transactions/begin"
        request_body = BeginTransactionRequest(
            transaction_type=transaction_type,
            origination=origination,
            expected_resource_count=expected_resource_count,
        )

        with RobotoHttpExceptionParse():
            response = self.__http_client.post(
                url,
                data=request_body.model_dump_json(exclude_none=True),
                headers=roboto_headers(
                    org_id=org_id,
                    user_id=caller,
                    resource_owner_id=resource_owner_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
            )

        return TransactionRecord.model_validate(response.from_json(json_path=["data"]))

    def get_transaction(
        self,
        transaction_id: str,
        org_id: typing.Optional[str] = None,
        resource_owner_id: typing.Optional[str] = None,
    ) -> TransactionRecord:
        url = f"{self.__roboto_service_base_url}/v2/transactions/id/{transaction_id}"
        with RobotoHttpExceptionParse():
            response = self.__http_client.get(
                url,
                headers=roboto_headers(
                    org_id=org_id,
                    resource_owner_id=resource_owner_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
            )

        return TransactionRecord.model_validate(response.from_json(json_path=["data"]))

    def is_transaction_complete(
        self,
        transaction_id: str,
        resource_owner_id: str,
    ) -> bool:
        url = f"{self.__roboto_service_base_url}/v2/transactions/id/{transaction_id}/completion"
        with RobotoHttpExceptionParse():
            response = self.__http_client.get(
                url,
                headers=roboto_headers(
                    resource_owner_id=resource_owner_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
            )

        return TransactionCompletionResponse.model_validate(
            response.from_json(json_path=["data"])
        ).is_complete
