import httpx
import os
from typing import Any, Dict, List
from urllib.parse import urljoin, quote

from .schemas import BoardActions


async def update_board_async(
        tenant: str, workspace: str, board_path: str,
        actions: List[Dict[str, Any]],
        collab_host_url: str = None):
    """Update a board asynchronously.

    Send a list of update actions to the collab server to modify a board.
    Actions is a list of action dicts that looks like this
    ```
    actions = [
        {"type": action_type_1, "payload": payload_1},
        {"type": action_type_2, "payload": payload_2},
        ...
    ]
    ```
    The supported action types are
     - "add_node", here the payload has to be a valid node dict.
     - "update_node", here the payload has to include at least the node id.
     - "remove_node", here the payload is `{"id": node_id}`.
     - "add_edge", here the payload has to be a valid edge dict.
     - "update_edge", here the payload has to include at least the edge id.
     - "remove_edge", here the payload is `{"id": edge_id}`.
     - "update_process_queue": this updates the bot card processing queue.
       The payload is `{"id": node_id, "continue_prompt": bool, "end": bool}`

    Check out the pydantic classes in halerium_utilities.collab.schemas
    for further reference on valid payloads.

    Warning: will return [200 OK] even if the board_path does not exist.

    Parameters
    ----------
    tenant : str
        The tenant key
    workspace : str
        The workspace id
    board_path : str
        The path to the board file on the workspace
    actions : List[Dict[str, Any]]
        The list of update actions. See Examples.
    collab_host_url : str, optional
        The collab server endpoint. Will be constructed based on env variables if not specified.


    Returns
    -------
    The httpx.AsyncClient.post coroutine object.

    Examples
    --------
    >>> tenant = "erium"
    >>> workspace = "64d226305db8ad0012d15004"
    >>> board_path = "/path/to/board.board"
    >>> actions = [{"type": "remove_node", "payload": {"id": "187519f3-09e8-440f-b4e7-7f114f36b423"}}]
    >>> await update_board_async(tenant, workspace, board_path, actions)
    <Response [200 OK]>
    """

    if collab_host_url is None:
        collab_host_url = os.getenv("COLLAB_HOST_URL", "")

    actions = BoardActions.validate(actions).dict(exclude_none=True)
    data = {"actions": actions}

    async with httpx.AsyncClient() as httpx_client:
        file_url = urljoin(collab_host_url, "/api/boards"
                           f"/{quote(tenant, safe='')}"
                           f"/{quote(workspace, safe='')}"
                           f"/{quote(board_path, safe='')}")

        return httpx_client.post(file_url, json=data)


def update_board(
        tenant: str, workspace: str, board_path: str,
        actions: List[Dict[str, Any]],
        collab_host_url: str = None):
    """Update a board synchronously.

    Send a list of update actions to the collab server to modify a board.
    Actions is a list of action dicts that looks like this
    ```
    actions = [
        {"type": action_type_1, "payload": payload_1},
        {"type": action_type_2, "payload": payload_2},
        ...
    ]
    ```
    The supported action types are
     - "add_node", here the payload has to be a valid node dict.
     - "update_node", here the payload has to include at least the node id.
     - "remove_node", here the payload is `{"id": node_id}`.
     - "add_edge", here the payload has to be a valid edge dict.
     - "update_edge", here the payload has to include at least the edge id.
     - "remove_edge", here the payload is `{"id": edge_id}`.
     - "update_process_queue": this updates the bot card processing queue.
       The payload is `{"id": node_id, "continue_prompt": bool, "end": bool}`

    Check out the pydantic classes in halerium_utilities.collab.schemas
    for further reference on valid payloads.

    Warning: will return [200 OK] even if the board_path does not exist.

    Parameters
    ----------
    tenant : str
        The tenant key
    workspace : str
        The workspace id
    board_path : str
        The path to the board file on the workspace
    actions : List[Dict[str, Any]]
        The list of update actions. See Examples.
    collab_host_url : str, optional
        The collab server endpoint. Will be constructed based on env variables if not specified.


    Returns
    -------
    The httpx.Response to the request.

    Examples
    --------
    >>> tenant = "erium"
    >>> workspace = "64d226305db8ad0012d15004"
    >>> board_path = "/path/to/board.board"
    >>> actions = [{"type": "remove_node", "payload": {"id": "187519f3-09e8-440f-b4e7-7f114f36b423"}}]
    >>> update_board(tenant, workspace, board_path, actions)
    <Response [200 OK]>
    """

    if collab_host_url is None:
        collab_host_url = os.getenv("COLLAB_HOST_URL", "")

    actions = BoardActions.validate(actions).dict(exclude_none=True)
    data = {"actions": actions}

    with httpx.Client() as httpx_client:
        file_url = urljoin(collab_host_url, "/api/boards"
                           f"/{quote(tenant, safe='')}"
                           f"/{quote(workspace, safe='')}"
                           f"/{quote(board_path, safe='')}")

        return httpx_client.post(file_url, json=data)


async def get_board_async(
        tenant: str, workspace: str, board_path: str,
        collab_host_url: str = None):
    """Get board asynchronously.

    Get the board as a json/dict.
    Check out the Board classes in halerium_utilities.board.schemas
    for further reference.

    Warning: will return an empty board if board_path does not exist.

    Parameters
    ----------
    tenant : str
        The tenant key
    workspace : str
        The workspace id
    board_path : str
        The path to the board file on the workspace
    collab_host_url : str, optional
        The collab server endpoint. Will be constructed based on env variables if not specified.

    Returns
    -------
    The httpx.AsyncClient.get coroutine object.

    Examples
    --------
    >>> tenant = "erium"
    >>> workspace = "64d226305db8ad0012d15004"
    >>> board_path = "/path/to/board.board"
    >>> await r = get_board_async(tenant, workspace, board_path, actions)
    >>> board = r.json()["data"]
    """

    if collab_host_url is None:
        collab_host_url = os.getenv("COLLAB_HOST_URL", "")

    async with httpx.AsyncClient() as httpx_client:
        file_url = urljoin(collab_host_url, "/api/boards"
                           f"/{quote(tenant, safe='')}"
                           f"/{quote(workspace, safe='')}"
                           f"/{quote(board_path, safe='')}")

        return httpx_client.get(file_url)


def get_board(
        tenant: str, workspace: str, board_path: str,
        collab_host_url: str = None):
    """Get board synchronously.

    Get the board as a json/dict.
    Check out the Board classes in halerium_utilities.board.schemas
    for further reference.

    Warning: will return an empty board if board_path does not exist.

    Parameters
    ----------
    tenant : str
        The tenant key
    workspace : str
        The workspace id
    board_path : str
        The path to the board file on the workspace
    collab_host_url : str, optional
        The collab server endpoint. Will be constructed based on env variables if not specified.

    Returns
    -------
    The httpx.AsyncClient.get coroutine object.

    Examples
    --------
    >>> tenant = "erium"
    >>> workspace = "64d226305db8ad0012d15004"
    >>> board_path = "/path/to/board.board"
    >>> r = get_board(tenant, workspace, board_path, actions)
    >>> board = r.json()["data"]
    """

    if collab_host_url is None:
        collab_host_url = os.getenv("COLLAB_HOST_URL", "")

    with httpx.Client() as httpx_client:
        file_url = urljoin(collab_host_url, "/api/boards"
                           f"/{quote(tenant, safe='')}"
                           f"/{quote(workspace, safe='')}"
                           f"/{quote(board_path, safe='')}")

        return httpx_client.get(file_url)

# TODO: create tests for these methods
