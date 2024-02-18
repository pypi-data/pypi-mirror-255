import httpx
import json
import os
from typing import Any, Dict
from urllib.parse import urljoin

from halerium_utilities.utils.sse import parse_sse_response, parse_sse_response_async


def _prepare_model_request(model_name: str, body: dict):
    """
    Prepare the httpx streaming parameters to load model results.

    Parameters
    ----------
    model_name The name of the model.
    body The body dict to be passed to the model.

    Returns
    -------
    A dict containing the httpx stream parameters (kwargs) for streaming model results.

    """

    tenant = os.getenv('HALERIUM_TENANT_KEY', '')
    workspace = os.getenv('HALERIUM_PROJECT_ID', '')
    runner_id = os.getenv('HALERIUM_ID', '')
    base_url = os.getenv('HALERIUM_BASE_URL', '')
    url = urljoin(base_url, "/api"
                            f"/tenants/{tenant}"
                            f"/projects/{workspace}"
                            f"/runners/{runner_id}"
                            "/models")

    headers = {'halerium-runner-token': os.getenv('HALERIUM_TOKEN', '')}

    payload = {
        "model_id": model_name,
        "body": body,
        "tenant": tenant,
        "workspace": workspace
    }

    return dict(
        method="POST",
        url=url,
        headers=headers,
        json=payload,
        timeout=120,
    )


async def call_model_async(
        model_name: str,
        body: Dict[str, Any],
        parse_data: bool = False):
    """Call model asynchronously from a Halerium runner.

    Calls the specified model with the given body.

    Parameters
    ----------
    model_name: str
        The model to use. Currently supported are "chat-gpt-35", "chat-gpt-40",
        "chat-gpt-40-large", "chat-gpt-40-turbo", "chat-gpt-40-turbo-vision", "llama2",
        "dall-e", "stability-ai/sdxl", "ada2-embedding".
    body: Dict[str, Any]
        The body for the model's request.
        See the examples.
    parse_data: bool, optional
        Whether to parse the SSE event data as json strings.
        The default is False.

    Returns
    -------
    async_generator
        The generator of the models answer as SSE events.

    Examples
    --------
    >>> body = {"messages": [{"role": "user", "content": "Hi!"}], "temperature": 0}
    >>> gen = models.call_model_async("chat-gpt-35", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')
    """

    async with httpx.AsyncClient() as httpx_client:
        async with httpx_client.stream(**_prepare_model_request(model_name, body)) as response:
            async for event in parse_sse_response_async(response):
                if parse_data:
                    event.data = json.loads(event.data)
                yield event


def call_model(
        model_name: str,
        body: Dict[str, Any],
        parse_data: bool = False):
    """Call model from a Halerium runner.

    Calls the specified model with the given body.

    Parameters
    ----------
    model_name: str
        The model to use. Currently supported are "chat-gpt-35", "chat-gpt-40",
        "chat-gpt-40-large", "chat-gpt-40-turbo", "chat-gpt-40-turbo-vision", "llama2",
        "dall-e", "stability-ai/sdxl", "ada2-embedding".
    body: Dict[str, Any]
        The body for the model's request.
        See the examples.
    parse_data: bool, optional
        Whether to parse the SSE event data as json strings.
        The default is False.

    Returns
    -------
    async_generator
        The generator of the models answer as SSE events.

    Examples
    --------
    >>> body = {"messages": [{"role": "user", "content": "Hi!"}], "temperature": 0}
    >>> gen = models.call_model("chat-gpt-35", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')
    """

    with httpx.Client() as httpx_client:
        with httpx_client.stream(**_prepare_model_request(model_name, body)) as response:
            for event in parse_sse_response(response):
                if parse_data:
                    event.data = json.loads(event.data)
                yield event

