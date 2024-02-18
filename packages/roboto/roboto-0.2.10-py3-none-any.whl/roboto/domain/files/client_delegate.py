import collections.abc
import pathlib
from typing import Any, Callable, Optional
import urllib.parse

import boto3
import boto3.s3.transfer as s3_transfer
import botocore.config
import botocore.credentials
import botocore.session

from ...exceptions import RobotoHttpExceptionParse
from ...http import (
    HttpClient,
    PaginatedList,
    roboto_headers,
)
from ...query import QuerySpecification
from ...serde import pydantic_jsonable_dict
from .delegate import (
    CredentialProvider,
    FileDelegate,
    FileTag,
)
from .progress import (
    NoopProgressMonitorFactory,
    ProgressMonitorFactory,
)
from .record import FileRecord

# Used to change between showing progress bars for every file and "uploading X files"
MANY_FILES = 100


class DynamicCallbackSubscriber(s3_transfer.BaseSubscriber):
    __on_done_cb: Optional[Callable[[Any], None]]
    __on_progress_cb: Optional[Callable[[Any], None]]
    __on_queued_cb: Optional[Callable[[Any], None]]

    def __init__(
        self,
        on_done_cb: Optional[Callable[[Any], None]] = None,
        on_progress_cb: Optional[Callable[[Any], None]] = None,
        on_queued_cb: Optional[Callable[[Any], None]] = None,
    ):
        self.__on_done_cb = on_done_cb
        self.__on_progress_cb = on_progress_cb
        self.__on_queued_cb = on_queued_cb

    def on_queued(self, future, **kwargs):
        if self.__on_queued_cb is not None:
            self.__on_queued_cb(future)

    def on_progress(self, future, bytes_transferred, **kwargs):
        if self.__on_progress_cb is not None:
            self.__on_progress_cb(future)

    def on_done(self, future, **kwargs):
        if self.__on_done_cb is not None:
            self.__on_done_cb(future)


class FileClientDelegate(FileDelegate):
    __http_client: HttpClient
    __roboto_service_base_url: str

    @staticmethod
    def generate_s3_client(
        credential_provider: CredentialProvider, tcp_keepalive: bool = True
    ):
        creds = credential_provider()
        refreshable_credentials = (
            botocore.credentials.RefreshableCredentials.create_from_metadata(
                metadata=creds,
                refresh_using=credential_provider,
                method="roboto-api",
            )
        )
        botocore_session = botocore.session.get_session()
        botocore_session._credentials = refreshable_credentials
        botocore_session.set_config_variable("region", creds["region"])
        session = boto3.Session(botocore_session=botocore_session)

        return session.client(
            "s3", config=botocore.config.Config(tcp_keepalive=tcp_keepalive)
        )

    def __init__(self, roboto_service_base_url: str, http_client: HttpClient) -> None:
        super().__init__()
        self.__http_client = http_client
        self.__roboto_service_base_url = roboto_service_base_url

    def delete_file(self, record: FileRecord) -> None:
        url = f"{self.__roboto_service_base_url}/v1/files/{record.file_id}"

        with RobotoHttpExceptionParse():
            self.__http_client.delete(
                url,
                headers=roboto_headers(
                    resource_owner_id=record.org_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
            )

    @staticmethod
    def __transfer_manager_for_client_provider(
        credential_provider: CredentialProvider, max_concurrency: int = 8
    ):
        s3_client = FileClientDelegate.generate_s3_client(credential_provider)
        transfer_config = s3_transfer.TransferConfig(
            use_threads=True, max_concurrency=max_concurrency
        )
        return s3_transfer.create_transfer_manager(s3_client, transfer_config)

    def download_file(
        self,
        record: FileRecord,
        local_path: pathlib.Path,
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client = FileClientDelegate.generate_s3_client(credential_provider)

        res = s3_client.head_object(Bucket=record.bucket, Key=record.key)
        download_bytes = int(res.get("ContentLength", 0))

        source = record.key.replace(f"{record.org_id}/datasets/", "")

        progress_monitor = progress_monitor_factory.download_monitor(
            source=source, size=download_bytes
        )
        try:
            s3_client.download_file(
                Bucket=record.bucket,
                Key=record.key,
                Filename=str(local_path),
                Callback=progress_monitor.update,
            )
        finally:
            progress_monitor.close()

    def __download_many_files(
        self,
        file_generator: collections.abc.Generator[
            tuple[FileRecord, pathlib.Path], None, None
        ],
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 8,
    ):
        transfer_manager = self.__transfer_manager_for_client_provider(
            credential_provider, max_concurrency
        )

        total_file_count = progress_monitor_factory.get_context().get(
            "total_file_count", 0
        )

        base_path = progress_monitor_factory.get_context().get("base_path", "?")

        progress_monitor = progress_monitor_factory.upload_monitor(
            source=f"{total_file_count} files from {base_path}",
            size=total_file_count,
            kwargs={"unit": "file"},
        )

        def on_done_cb(future):
            progress_monitor.update(1)

        subscriber = DynamicCallbackSubscriber(on_done_cb=on_done_cb)

        with transfer_manager:
            for record, local_path in file_generator:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                transfer_manager.download(
                    record.bucket,
                    record.key,
                    str(local_path),
                    subscribers=[subscriber],
                )
        progress_monitor.close()

    def download_files(
        self,
        file_generator: collections.abc.Generator[
            tuple[FileRecord, pathlib.Path], None, None
        ],
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 8,
    ) -> None:
        total_file_count = progress_monitor_factory.get_context().get(
            "total_file_count", 0
        )

        if total_file_count >= 20:
            self.__download_many_files(
                file_generator,
                credential_provider,
                progress_monitor_factory,
                max_concurrency,
            )
        else:
            for record, local_path in file_generator:
                self.download_file(
                    record, local_path, credential_provider, progress_monitor_factory
                )

    def get_record_by_primary_key(
        self, file_id: str, org_id: Optional[str] = None
    ) -> FileRecord:
        url = f"{self.__roboto_service_base_url}/v1/files/record/{file_id}"

        with RobotoHttpExceptionParse():
            res = self.__http_client.get(
                url,
                headers=roboto_headers(
                    additional_headers={"Content-Type": "application/json"},
                ),
            )
        return FileRecord.model_validate(res.from_json(json_path=["data"]))

    def get_signed_url(
        self,
        record: FileRecord,
        override_content_disposition: Optional[str] = None,
        override_content_type: Optional[str] = None,
    ) -> str:
        url = f"{self.__roboto_service_base_url}/v1/files/{record.file_id}/signed-url"

        query_params: dict[str, str] = {}

        if override_content_disposition:
            query_params["override_content_disposition"] = override_content_disposition

        if override_content_type:
            query_params["override_content_type"] = override_content_type

        if len(query_params.keys()) > 0:
            url += "?" + urllib.parse.urlencode(query_params)

        with RobotoHttpExceptionParse():
            res = self.__http_client.get(
                url,
                headers=roboto_headers(
                    org_id=record.org_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
            )
        return res.from_json(json_path=["data", "url"])

    def query_files(
        self,
        query: QuerySpecification,
        org_id: Optional[str] = None,
    ) -> PaginatedList[FileRecord]:
        url = f"{self.__roboto_service_base_url}/v1/files/query"
        post_body = pydantic_jsonable_dict(query, exclude_none=True)
        with RobotoHttpExceptionParse():
            res = self.__http_client.post(
                url,
                data=post_body,
                headers=roboto_headers(
                    resource_owner_id=org_id,
                    additional_headers={"Content-Type": "application/json"},
                ),
                idempotent=True,
            )

        unmarshalled = res.from_json(json_path=["data"])
        return PaginatedList(
            items=[
                FileRecord.model_validate(dataset) for dataset in unmarshalled["items"]
            ],
            next_token=unmarshalled["next_token"],
        )

    def upload_file(
        self,
        local_path: pathlib.Path,
        bucket: str,
        key: str,
        credential_provider: CredentialProvider,
        tags: Optional[dict[FileTag, str]] = None,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        upload_file_args: dict[str, Any] = {
            "Filename": str(local_path),
            "Key": key,
            "Bucket": bucket,
        }

        if tags is not None:
            serializable_tags = {tag.value: value for tag, value in tags.items()}
            encoded_tags = urllib.parse.urlencode(serializable_tags)
            upload_file_args["ExtraArgs"] = {"Tagging": encoded_tags}

        progress_monitor = progress_monitor_factory.upload_monitor(
            source=key, size=local_path.stat().st_size
        )
        upload_file_args["Callback"] = progress_monitor.update

        try:
            s3_client = FileClientDelegate.generate_s3_client(credential_provider)
            s3_client.upload_file(**upload_file_args)
        finally:
            if progress_monitor is not None:
                progress_monitor.close()

    def __upload_many_files(
        self,
        bucket: str,
        file_generator: collections.abc.Generator[tuple[pathlib.Path, str], None, None],
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 20,
        extra_args: Optional[dict[str, Any]] = None,
    ):
        transfer_manager = self.__transfer_manager_for_client_provider(
            credential_provider, max_concurrency
        )

        base_path = progress_monitor_factory.get_context().get("base_path", "?")
        expected_file_count = progress_monitor_factory.get_context().get(
            "expected_file_count", "?"
        )
        expected_file_size = progress_monitor_factory.get_context().get(
            "expected_file_size", -1
        )

        progress_monitor = progress_monitor_factory.upload_monitor(
            source=f"{expected_file_count} files from {base_path}",
            size=expected_file_size,
        )

        try:
            for src, key in file_generator:
                transfer_manager.upload(
                    str(src),
                    bucket,
                    key,
                    extra_args=extra_args,
                    subscribers=[
                        s3_transfer.ProgressCallbackInvoker(progress_monitor.update)
                    ],
                )

            transfer_manager.shutdown()
        finally:
            progress_monitor.close()

    def upload_files(
        self,
        bucket: str,
        file_generator: collections.abc.Generator[tuple[pathlib.Path, str], None, None],
        credential_provider: CredentialProvider,
        tags: Optional[dict[FileTag, str]] = None,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 20,
    ) -> None:
        extra_args: Optional[dict[str, Any]] = None
        if tags is not None:
            serializable_tags = {tag.value: value for tag, value in tags.items()}
            encoded_tags = urllib.parse.urlencode(serializable_tags)
            extra_args = {"Tagging": encoded_tags}

        expected_file_count = progress_monitor_factory.get_context().get(
            "expected_file_count", "?"
        )

        if expected_file_count >= MANY_FILES:
            self.__upload_many_files(
                bucket=bucket,
                file_generator=file_generator,
                credential_provider=credential_provider,
                progress_monitor_factory=progress_monitor_factory,
                max_concurrency=max_concurrency,
                extra_args=extra_args,
            )
        else:
            for src, key in file_generator:
                self.upload_file(
                    local_path=src,
                    bucket=bucket,
                    key=key,
                    credential_provider=credential_provider,
                    tags=tags,
                    progress_monitor_factory=progress_monitor_factory,
                )
