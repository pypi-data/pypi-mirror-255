import json
import multiprocessing.connection
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Any

from amsdal_agent.constants import ALLOWED_ACTIONS
from amsdal_agent.queues.base import QueueBase
from amsdal_agent.services.options import AmsdaldOptions


def run_server(
    pipe: multiprocessing.connection.Connection,
    options: AmsdaldOptions,
    queue: QueueBase,
) -> None:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            options.logger.debug(
                'Server::do_POST()::method: %s, path: %s, data: %s', self.command, self.path, post_data
            )

            if self.path == '/action':
                action = post_data.decode()

                if action in ALLOWED_ACTIONS:
                    options.logger.info('Server::do_POST()::action: %s', action)
                    pipe.send(action)
            elif self.path == '/data':
                data: dict[str, Any] = json.loads(post_data)
                options.logger.debug(
                    'Server:: pre put data to queue: %s',
                    data,
                )
                queue.put(data)
                options.logger.debug(
                    'Server::put data to queue',
                )

            self.send_response(200, message='OK')
            self.end_headers()

    host: str
    port: int

    try:
        host, _port = options.server_host.split(':')
        port = int(_port)
    except ValueError:
        host = options.server_host
        port = 8000

    options.logger.info(f'Starting server on http://{host}:{port}')
    server = HTTPServer((host, port), RequestHandler)
    server.serve_forever()
