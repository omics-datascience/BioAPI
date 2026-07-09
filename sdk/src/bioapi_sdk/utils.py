from __future__ import annotations

import os
from typing import Any, Final, Mapping
from urllib.parse import urljoin

import requests


DEFAULT_BASE_URL: Final[str] = os.getenv(
    "BIOAPI_BASE_URL", "https://bioapi.multiomix.org"
)


class BioAPIRequestError(RuntimeError):
    """Raised when BioAPI returns a non-success response or invalid JSON."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        url: str | None = None,
        response: requests.Response | None = None,
    ) -> None:
        """Initialize a BioAPI request error.

        :param message: Error message reported by BioAPI or the client.
        :param status_code: HTTP status code returned by BioAPI.
        :param url: Final URL requested.
        :param response: Raw `requests.Response` object.
        """
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response = response


def build_url(endpoint: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Return an absolute BioAPI URL from a documented endpoint path.

    :param endpoint: Absolute URL or documented BioAPI endpoint path.
    :param base_url: Base BioAPI URL used when `endpoint` is relative.
    :returns: Absolute URL for the endpoint.
    """
    if endpoint.startswith(("http://", "https://")):
        return endpoint

    return urljoin(f"{base_url.rstrip('/')}/", endpoint.lstrip("/"))


def request_api_response(
    url: str,
    method: str = "GET",
    params: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Any:
    """Request a documented BioAPI endpoint and return its JSON response.

    BioAPI endpoints return JSON for successful responses and JSON objects with an
    `error` key for 400, 404, and 500 responses. If an upstream gateway returns
    an HTML error page instead (for example, a 502 response), the raised error
    identifies BioAPI as unavailable rather than reporting a JSON parsing error.

    :param url: Absolute URL or documented BioAPI endpoint path.
    :param method: HTTP method. BioAPI documents `GET` and `POST` endpoints.
    :param params: Query string parameters for `GET` requests.
    :param body: JSON body for `POST` requests.
    :param base_url: Base BioAPI URL used when `url` is relative.
    :param timeout: Request timeout in seconds.
    :param session: Optional `requests.Session` used to send the request.
    :returns: Decoded JSON response payload.
    :raises ValueError: If `method` is not `GET` or `POST`.
    :raises BioAPIRequestError: If BioAPI returns an error or invalid JSON.
    """
    request_method = method.upper()
    if request_method not in {"GET", "POST"}:
        raise ValueError("BioAPI documentation only describes GET and POST endpoints.")

    request = session.request if session is not None else requests.request
    response = request(
        request_method,
        build_url(url, base_url),
        params=params,
        json=body if request_method == "POST" else None,
        timeout=timeout,
    )

    if not response.ok:
        try:
            payload = response.json()
        except ValueError as exc:
            reason = f" {response.reason}" if response.reason else ""
            raise BioAPIRequestError(
                (
                    "BioAPI is currently unavailable "
                    f"(HTTP {response.status_code}{reason})."
                ),
                status_code=response.status_code,
                url=response.url,
                response=response,
            ) from exc

        message = (
            payload.get("error", response.reason)
            if isinstance(payload, dict)
            else response.reason
        )
        raise BioAPIRequestError(
            str(message),
            status_code=response.status_code,
            url=response.url,
            response=response,
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise BioAPIRequestError(
            "BioAPI response was not valid JSON.",
            status_code=response.status_code,
            url=response.url,
            response=response,
        ) from exc

    return payload


def get_api_response(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Any:
    """Request a documented GET endpoint and return its JSON response.

    :param url: Absolute URL or documented BioAPI endpoint path.
    :param params: Query string parameters for the request.
    :param base_url: Base BioAPI URL used when `url` is relative.
    :param timeout: Request timeout in seconds.
    :param session: Optional `requests.Session` used to send the request.
    :returns: Decoded JSON response payload.
    """
    return request_api_response(
        url,
        method="GET",
        params=params,
        base_url=base_url,
        timeout=timeout,
        session=session,
    )


def post_api_response(
    url: str,
    *,
    body: Mapping[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Any:
    """Request a documented POST endpoint with a JSON body.

    :param url: Absolute URL or documented BioAPI endpoint path.
    :param body: JSON body for the request.
    :param base_url: Base BioAPI URL used when `url` is relative.
    :param timeout: Request timeout in seconds.
    :param session: Optional `requests.Session` used to send the request.
    :returns: Decoded JSON response payload.
    """
    return request_api_response(
        url,
        method="POST",
        body=body,
        base_url=base_url,
        timeout=timeout,
        session=session,
    )
