import abc
import collections.abc
import enum
import pathlib
from typing import Callable, Optional, TypedDict

# Python 3.8/3.9 compatible import of TypeAlias
try:
    from typing import TypeAlias
except ImportError:
    try:
        from typing_extensions import TypeAlias
    except ImportError:
        pass

from ...http import PaginatedList
from ...query import QuerySpecification
from .progress import (
    NoopProgressMonitorFactory,
    ProgressMonitorFactory,
)
from .record import FileRecord


class FileTag(enum.Enum):
    DatasetId = "dataset_id"
    OrgId = "org_id"
    # Path to file relative to common prefix
    CommonPrefix = "common_prefix"
    TransactionId = "transaction_id"


class S3Credentials(TypedDict):
    """
    This interface is driven by botocore.credentials.RefreshableCredentials
    """

    access_key: str
    secret_key: str
    token: str
    region: str
    expiry_time: Optional[str]


CredentialProvider: TypeAlias = Callable[[], S3Credentials]


class FileDelegate(abc.ABC):
    @abc.abstractmethod
    def delete_file(self, record: FileRecord) -> None:
        raise NotImplementedError("delete_file")

    @abc.abstractmethod
    def download_file(
        self,
        record: FileRecord,
        local_path: pathlib.Path,
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        raise NotImplementedError("download_file")

    @abc.abstractmethod
    def download_files(
        self,
        file_generator: collections.abc.Generator[
            tuple[FileRecord, pathlib.Path], None, None
        ],
        credential_provider: CredentialProvider,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 20,
    ) -> None:
        raise NotImplementedError("download_files")

    @abc.abstractmethod
    def get_record_by_primary_key(self, file_id: str) -> FileRecord:
        raise NotImplementedError("get_record_by_primary_key")

    @abc.abstractmethod
    def get_signed_url(
        self,
        record: FileRecord,
        override_content_disposition: Optional[str] = None,
        override_content_type: Optional[str] = None,
    ) -> str:
        raise NotImplementedError("get_signed_url")

    @abc.abstractmethod
    def query_files(
        self,
        query: QuerySpecification,
        org_id: Optional[str] = None,
    ) -> PaginatedList[FileRecord]:
        raise NotImplementedError("query_files")

    @abc.abstractmethod
    def upload_file(
        self,
        local_path: pathlib.Path,
        bucket: str,
        key: str,
        credential_provider: CredentialProvider,
        tags: Optional[dict[FileTag, str]] = None,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        raise NotImplementedError("upload_file")

    @abc.abstractmethod
    def upload_files(
        self,
        bucket: str,
        file_generator: collections.abc.Generator[tuple[pathlib.Path, str], None, None],
        credential_provider: CredentialProvider,
        tags: Optional[dict[FileTag, str]] = None,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
        max_concurrency: int = 1,
    ) -> None:
        raise NotImplementedError("upload_file")
