import random
from http import HTTPStatus
from time import sleep
from typing import Any, Dict

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_error import HttpError
from ...models.http_validation_error import HTTPValidationError
from ...models.integration_key_out import IntegrationKeyOut
from ...types import Response

SLEEP_TIME = 0.05
NUM_RETRIES = 3


def _get_kwargs(
    app_id: str,
    integ_id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/api/v1/app/{app_id}/integration/{integ_id}/key/".format(client.base_url, app_id=app_id, integ_id=integ_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> IntegrationKeyOut:
    if response.status_code == HTTPStatus.OK:
        response_200 = IntegrationKeyOut.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise HttpError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise HttpError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.FORBIDDEN:
        raise HttpError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.NOT_FOUND:
        raise HttpError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.CONFLICT:
        raise HttpError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        raise HTTPValidationError.init_exception(response.json(), response.status_code)
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise HttpError.init_exception(response.json(), response.status_code)
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(*, client: Client, response: httpx.Response) -> Response[IntegrationKeyOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app_id: str,
    integ_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[IntegrationKeyOut]:
    """Get Integration Key

     Get an integration's key.

    Args:
        app_id (str): The app's ID or UID Example: unique-app-identifier.
        integ_id (str): The integ's ID Example: integ_1srOrx2ZWZBpBUvZwXKQmoEYga2.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IntegrationKeyOut]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        integ_id=integ_id,
        client=client,
    )

    kwargs["headers"] = {"svix-req-id": f"{random.getrandbits(32)}", **kwargs["headers"]}

    for retry_count in range(NUM_RETRIES):
        response = httpx.request(
            verify=client.verify_ssl,
            **kwargs,
        )
        if response.status_code >= 500:
            kwargs["headers"]["svix-retry-count"] = str(retry_count)
            sleep(SLEEP_TIME * (2**retry_count))
        else:
            break

    return _build_response(client=client, response=response)


def sync(
    app_id: str,
    integ_id: str,
    *,
    client: AuthenticatedClient,
) -> IntegrationKeyOut:
    """Get Integration Key

     Get an integration's key.

    Args:
        app_id (str): The app's ID or UID Example: unique-app-identifier.
        integ_id (str): The integ's ID Example: integ_1srOrx2ZWZBpBUvZwXKQmoEYga2.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IntegrationKeyOut
    """

    return sync_detailed(
        app_id=app_id,
        integ_id=integ_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    app_id: str,
    integ_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[IntegrationKeyOut]:
    """Get Integration Key

     Get an integration's key.

    Args:
        app_id (str): The app's ID or UID Example: unique-app-identifier.
        integ_id (str): The integ's ID Example: integ_1srOrx2ZWZBpBUvZwXKQmoEYga2.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IntegrationKeyOut]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        integ_id=integ_id,
        client=client,
    )

    kwargs["headers"] = {"svix-req-id": f"{random.getrandbits(32)}", **kwargs["headers"]}

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        for retry_count in range(NUM_RETRIES):
            response = await _client.request(**kwargs)
            if response.status_code >= 500:
                kwargs["headers"]["svix-retry-count"] = str(retry_count)
                sleep(SLEEP_TIME * (2**retry_count))
            else:
                break

    return _build_response(client=client, response=response)


async def asyncio(
    app_id: str,
    integ_id: str,
    *,
    client: AuthenticatedClient,
) -> IntegrationKeyOut:
    """Get Integration Key

     Get an integration's key.

    Args:
        app_id (str): The app's ID or UID Example: unique-app-identifier.
        integ_id (str): The integ's ID Example: integ_1srOrx2ZWZBpBUvZwXKQmoEYga2.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IntegrationKeyOut
    """

    return (
        await asyncio_detailed(
            app_id=app_id,
            integ_id=integ_id,
            client=client,
        )
    ).parsed
