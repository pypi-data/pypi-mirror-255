from time import sleep
from typing import Any

import httpx

from amsdal_agent.queues.base import QueueBase
from amsdal_agent.services.options import AmsdaldOptions


def run_worker(
    options: AmsdaldOptions,
    queue: QueueBase,
) -> None:
    # Initialize the HTTP client
    client = httpx.Client(timeout=60)
    headers = {}

    if options.app_auth:
        headers['Authorization'] = f'Token {options.app_auth}'

    retry_message = None
    retry_count = 0

    while True:
        message = retry_message or queue.get()
        request = build_request_from_action(options, message, headers)
        response: httpx.Response | None = None

        if not request:
            queue.task_done()
            continue

        # Send the message via the HTTP client
        try:
            response = client.send(request)
            response.raise_for_status()
        except httpx.HTTPError as e:
            queue.task_failed(message)
            retry_message = message
            retry_count += 1
            countdown = min(retry_count**2, 60)
            options.logger.error(
                'Failed to send data: %s. Response: %s. Retry in %s seconds',
                e,
                response.content if response else 'No Response',
                countdown,
            )
            sleep(countdown)
        else:
            retry_message = None
            retry_count = 0
            queue.task_done()


def build_request_from_action(
    options: AmsdaldOptions,
    message: dict[str, Any],
    headers: dict[str, str],
) -> httpx.Request | None:
    app_host = options.app_host
    method = 'POST'
    action: str = message['action']
    params: dict[str, Any] = message.get('params') or {}
    path_params: list[Any] = message.get('path_params') or []
    data: dict[str, Any] | None = message.get('data')

    match action:
        case 'register_schema':
            url_path = '/api/classes/'
        case 'unregister_schema':
            url_path = '/api/classes/{}/'.format(*path_params)
            method = 'DELETE'
        case 'object_create':
            url_path = '/api/objects/'
        case 'object_update':
            url_path = '/api/objects/{}/'.format(*path_params)
        case 'object_delete':
            method = 'DELETE'
            url_path = '/api/objects/{}/'.format(*path_params)
        case _:
            options.logger.warning('Unknown action: %s', action)
            return None

    request_params: dict[str, Any] = {
        'method': method,
        'url': f'{app_host}{url_path}',
        'headers': headers,
    }

    if params:
        request_params['params'] = params

    if data:
        request_params['json'] = data

    options.logger.info('Integration worker: Request: %s', request_params)

    return httpx.Request(**request_params)
