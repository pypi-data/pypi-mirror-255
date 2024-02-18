import errno
import http
import http.client
import json
import logging
import random
import typing
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

import tenacity
import tenacity.wait

from roboto.exceptions import (
    ClientError,
    HttpError,
    ServerError,
)

from ..logging import LOGGER_NAME
from ..serde import safe_dict_drill

logger = logging.getLogger(LOGGER_NAME)

DEFAULT_HEADERS = object()


RetryWaitFn = typing.Callable[
    [tenacity.RetryCallState, typing.Optional[BaseException]], float
]


def default_retry_wait_ms(
    retry_state: tenacity.RetryCallState, _exc: typing.Optional[BaseException]
) -> float:
    exponential_wait = 500 * (1.5 ** (retry_state.attempt_number - 1))
    jittered = exponential_wait * random.uniform(0.9, 1.1)
    return min(jittered, 30_000)


class HttpResponse:
    __response: urllib.response.addinfourl

    def __init__(self, response: urllib.response.addinfourl) -> None:
        super().__init__()
        self.__response = response

    @property
    def readable_response(self) -> urllib.response.addinfourl:
        return self.__response

    @property
    def status(self) -> http.HTTPStatus:
        status_code = self.__response.status
        if status_code is None:
            raise RuntimeError("Response has no status code")
        return http.HTTPStatus(int(status_code))

    @property
    def headers(self) -> typing.Optional[dict[str, str]]:
        return dict(self.__response.headers.items())

    def from_json(self, json_path: typing.Optional[list[str]] = None) -> typing.Any:
        with self.__response:
            unmarsalled = json.loads(self.__response.read().decode("utf-8"))
            if json_path is None:
                return unmarsalled

            return safe_dict_drill(unmarsalled, json_path)

    def from_string(self):
        with self.__response:
            return self.__response.read().decode("utf-8")


class HttpRequest:
    url: str
    method: str
    headers: dict
    retry_wait: RetryWaitFn
    data: typing.Any = None
    idempotent: bool = False

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: typing.Optional[dict[str, str]] = None,
        data: typing.Any = None,
        retry_wait: typing.Optional[RetryWaitFn] = None,
        idempotent: bool = False,
    ):
        self.url = url
        self.method = method
        self.headers = headers if headers is not None else {}
        self.data = data
        self.retry_wait = (
            retry_wait if retry_wait is not None else default_retry_wait_ms
        )
        self.idempotent = idempotent

    def __repr__(self) -> str:
        return (
            f"HttpRequest("
            f"url={self.url}, "
            f"method={self.method}, "
            f"headers={self.headers}, "
            f"data={self.data}, "
            f"idempotent={self.idempotent}"
            ")"
        )

    @property
    def body(self) -> typing.Optional[bytes]:
        if self.data is None:
            return None

        if isinstance(self.data, bytes):
            return self.data

        if isinstance(self.data, str):
            return self.data.encode("utf-8")

        return json.dumps(self.data).encode("utf-8")

    @property
    def hostname(self) -> str:
        parsed_url = urllib.parse.urlparse(self.url)
        return (
            parsed_url.hostname
            if parsed_url.hostname is not None
            else parsed_url.netloc
        )

    def append_headers(self, headers: dict[str, str]) -> None:
        self.headers.update(headers)


HttpRequestDecorator = typing.Callable[[HttpRequest], HttpRequest]


class is_expected_to_be_transient:
    """Retry predicate that returns True if the exception is expected to be transient."""

    __request: HttpRequest

    def __init__(self, request: HttpRequest):
        self.__request = request

    def __call__(self, exc: typing.Any) -> bool:
        if isinstance(exc, http.client.RemoteDisconnected):
            logger.warning("Remote host closed connection", exc_info=exc)
            if not self.__request_expected_to_be_idempotent():
                # Request may have be processed, we don't know.
                return False

            return True

        if isinstance(exc, urllib.error.HTTPError):
            try:
                status_code = http.HTTPStatus(int(exc.code))

                if not self.__request_expected_to_be_idempotent():
                    # 500 and 504 are not safe to retry if the request is not idempotent
                    if status_code in (
                        http.HTTPStatus.REQUEST_TIMEOUT,
                        http.HTTPStatus.INTERNAL_SERVER_ERROR,
                        http.HTTPStatus.GATEWAY_TIMEOUT,
                    ):
                        return False

                return status_code in (
                    http.HTTPStatus.REQUEST_TIMEOUT,
                    http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    http.HTTPStatus.TOO_MANY_REQUESTS,
                    http.HTTPStatus.BAD_GATEWAY,
                    http.HTTPStatus.SERVICE_UNAVAILABLE,
                    http.HTTPStatus.GATEWAY_TIMEOUT,
                )
            except ValueError:
                return False

        # Must come after the isinstance check of HTTPError,
        # which is a subclass of URLError
        if isinstance(exc, urllib.error.URLError):
            # Connection reset by peer, probably transient
            conn_reset_error = (
                isinstance(exc.reason, OSError) and exc.reason.errno == errno.ECONNRESET
            ) or "Connection reset by peer" in str(exc.reason)
            if conn_reset_error and self.__request_expected_to_be_idempotent():
                return True

            # DNS error, probably transient
            return "Temporary failure in name resolution" in str(exc.reason)

        return False

    def __request_expected_to_be_idempotent(self) -> bool:
        return self.__request.idempotent is True


class HttpClient:
    __base_headers: dict[str, str]
    __default_auth: typing.Optional[HttpRequestDecorator]
    __default_endpoint: typing.Optional[str]

    def __init__(
        self,
        base_headers: typing.Optional[dict[str, str]] = None,
        default_endpoint: typing.Optional[str] = None,
        default_auth: typing.Optional[HttpRequestDecorator] = None,
    ):
        self.__base_headers = base_headers if base_headers is not None else {}
        self.__default_auth = default_auth
        self.__default_endpoint = default_endpoint

    def delete(
        self,
        url,
        data: typing.Any = None,
        headers: typing.Optional[dict] = None,
        idempotent: bool = True,
    ) -> HttpResponse:
        request = HttpRequest(
            url=url, method="DELETE", data=data, headers=headers, idempotent=idempotent
        )
        return self.__request(request)

    def get(
        self,
        url: str,
        headers: typing.Optional[dict] = None,
        retry_wait: RetryWaitFn = default_retry_wait_ms,
        idempotent: bool = True,
    ) -> HttpResponse:
        request = HttpRequest(
            url=url,
            method="GET",
            headers=headers,
            retry_wait=retry_wait,
            idempotent=idempotent,
        )
        return self.__request(request)

    def post(
        self,
        url,
        data: typing.Any = None,
        headers: typing.Optional[dict] = None,
        idempotent: bool = False,
    ) -> HttpResponse:
        request = HttpRequest(
            url=url, method="POST", data=data, headers=headers, idempotent=idempotent
        )
        return self.__request(request)

    def patch(
        self,
        url,
        data: typing.Any = None,
        headers: typing.Optional[dict] = None,
        idempotent: bool = True,
    ) -> HttpResponse:
        request = HttpRequest(
            url=url, method="PATCH", data=data, headers=headers, idempotent=idempotent
        )
        return self.__request(request)

    def put(
        self,
        url,
        data: typing.Any = None,
        headers: typing.Optional[dict] = None,
        idempotent: bool = True,
    ) -> HttpResponse:
        request = HttpRequest(
            url=url, method="PUT", data=data, headers=headers, idempotent=idempotent
        )
        return self.__request(request)

    def url(self, path: str) -> str:
        if self.__default_endpoint is None:
            raise ValueError(
                "HttpClient.url called for client with no default endpoint."
            )
        return f"{self.__default_endpoint}/{path}"

    def __request(self, request_ctx: HttpRequest) -> HttpResponse:
        if self.__default_auth is not None:
            request_ctx = self.__default_auth(request_ctx)

        logger.debug("%s", request_ctx)

        headers = self.__base_headers.copy()
        if request_ctx.headers:
            headers.update(request_ctx.headers)

        try:
            for attempt in tenacity.Retrying(
                retry=tenacity.retry_if_exception(
                    is_expected_to_be_transient(request_ctx)
                ),
                stop=tenacity.stop_after_attempt(10),
                reraise=True,
                wait=self._wait(request_ctx.retry_wait),
            ):
                with attempt:
                    request = urllib.request.Request(
                        request_ctx.url, method=request_ctx.method
                    )

                    req_body = request_ctx.body
                    if req_body is not None:
                        request.data = req_body

                    for key, value in headers.items():
                        request.add_header(key, value)

                    return HttpResponse(urllib.request.urlopen(request))
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            if status_code > 399 and status_code < 500:
                raise ClientError(exc) from None
            elif status_code > 499:
                raise ServerError(exc) from None
            else:
                raise HttpError(exc) from None
        except urllib.error.URLError as exc:
            if (
                isinstance(exc.reason, OSError)
                and exc.reason.errno == errno.ECONNREFUSED
            ):
                raise ConnectionRefusedError(
                    f"Couldn't connect to endpoint {request_ctx.url}"
                ) from None
            else:
                raise
        except Exception:
            raise

        raise RuntimeError("Unreachable")

    def _wait(self, waiter: RetryWaitFn) -> tenacity.wait.wait_base:
        class Waiter(tenacity.wait.wait_base):
            def __call__(self, retry_state: tenacity.RetryCallState) -> float:
                return waiter(retry_state, None) / 1000

        return Waiter()
