from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.llm_validate_request import LLMValidateRequest
from ...models.validation_result import ValidationResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: LLMValidateRequest,
    log: Union[Unset, bool] = True,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    params: Dict[str, Any] = {}

    params["log"] = log

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/validate/llm",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ValidationResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ValidationResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ValidationResult.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, ValidationResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LLMValidateRequest,
    log: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ValidationResult]]:
    """Validate a single prompt/response pair

     This endpoint can be used to synchronously get validation results from a single input
    prompt/response. It automatically performs whylogs profiling and sends profiles to
    whylabs in the background, just like  the /log endpoint.

    Args:
        log (bool, optional): Determines if logging to WhyLabs is enabled for the validate request.
    Defaults to True.

    Args:
        log (Union[Unset, bool]):  Default: True.
        body (LLMValidateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ValidationResult]]
    """

    kwargs = _get_kwargs(
        body=body,
        log=log,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LLMValidateRequest,
    log: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ValidationResult]]:
    """Validate a single prompt/response pair

     This endpoint can be used to synchronously get validation results from a single input
    prompt/response. It automatically performs whylogs profiling and sends profiles to
    whylabs in the background, just like  the /log endpoint.

    Args:
        log (bool, optional): Determines if logging to WhyLabs is enabled for the validate request.
    Defaults to True.

    Args:
        log (Union[Unset, bool]):  Default: True.
        body (LLMValidateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ValidationResult]
    """

    return sync_detailed(
        client=client,
        body=body,
        log=log,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LLMValidateRequest,
    log: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ValidationResult]]:
    """Validate a single prompt/response pair

     This endpoint can be used to synchronously get validation results from a single input
    prompt/response. It automatically performs whylogs profiling and sends profiles to
    whylabs in the background, just like  the /log endpoint.

    Args:
        log (bool, optional): Determines if logging to WhyLabs is enabled for the validate request.
    Defaults to True.

    Args:
        log (Union[Unset, bool]):  Default: True.
        body (LLMValidateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ValidationResult]]
    """

    kwargs = _get_kwargs(
        body=body,
        log=log,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LLMValidateRequest,
    log: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ValidationResult]]:
    """Validate a single prompt/response pair

     This endpoint can be used to synchronously get validation results from a single input
    prompt/response. It automatically performs whylogs profiling and sends profiles to
    whylabs in the background, just like  the /log endpoint.

    Args:
        log (bool, optional): Determines if logging to WhyLabs is enabled for the validate request.
    Defaults to True.

    Args:
        log (Union[Unset, bool]):  Default: True.
        body (LLMValidateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ValidationResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            log=log,
        )
    ).parsed
