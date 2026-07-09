from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urljoin

import requests


DEFAULT_BASE_URL = "https://bioapi.multiomix.org"


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
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response = response


def build_url(endpoint: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Return an absolute BioAPI URL from a documented endpoint path."""
    if endpoint.startswith(("http://", "https://")):
        return endpoint

    return urljoin(f"{base_url.rstrip('/')}/", endpoint.lstrip("/"))


def request_api_response(
    url: str,
    *,
    method: str = "GET",
    params: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Any:
    """
    Request a documented BioAPI endpoint and return the decoded JSON response.

    BioAPI endpoints return JSON for successful responses and JSON objects with an
    ``error`` key for 400, 404, and 500 responses.
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

    try:
        payload = response.json()
    except ValueError as exc:
        raise BioAPIRequestError(
            "BioAPI response was not valid JSON.",
            status_code=response.status_code,
            url=response.url,
            response=response,
        ) from exc

    if not response.ok:
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

    return payload


def get_api_response(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Any:
    """Request a documented GET endpoint and return its JSON response."""
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
    """Request a documented POST endpoint with a JSON body and return JSON."""
    return request_api_response(
        url,
        method="POST",
        body=body,
        base_url=base_url,
        timeout=timeout,
        session=session,
    )
