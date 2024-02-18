import multiprocessing
import multiprocessing.connection
import os
import signal
import time
from typing import Any

from amsdal_agent.queues.manager import QueueManager
from amsdal_agent.services.options import AmsdaldOptions
from amsdal_agent.services.server import run_server


class ServerProcess:
    name = 'Amsdald Server'

    def __init__(
        self,
        options: AmsdaldOptions,
    ) -> None:
        self.process: multiprocessing.Process | None = None
        self.options = options
        self.read_pipe, self.write_pipe = multiprocessing.Pipe(duplex=False)

    def start(self) -> None:
        self.process = multiprocessing.Process(
            target=self.serve,
            args=(
                self.write_pipe,
                self.options.get_subprocess_init_kwargs('server'),
                QueueManager.get_queue_kwargs(),
            ),
            name=self.name,
        )

        self.process.start()

    def stop(self) -> None:
        if self.process and self.process.is_alive():
            # Send a signal to the process
            if self.process.pid:
                os.kill(self.process.pid, signal.SIGUSR1)

            # Give the process some time to handle the signal
            time.sleep(1)

            # Terminate the process
            self.process.terminate()
            self.process.join()

        self.process = None

    def close_pipes(self) -> None:
        self.read_pipe.close()
        self.write_pipe.close()

    @staticmethod
    def serve(
        pipe: multiprocessing.connection.Connection,
        options_kwargs: dict[str, Any],
        queue_kwargs: dict[str, Any],
    ) -> None:
        options = AmsdaldOptions(**options_kwargs)
        queue = None

        def signal_handler(signum: Any, frame: Any) -> None:  # noqa: ARG001
            options.logger.debug('Integration: Received signal: %s', signum)

            if queue:
                queue.teardown()

        signal.signal(signal.SIGUSR1, signal_handler)

        try:
            options.setup()
            options.logger.debug('Integration: Starting server.... PID: %s', os.getpid())
            queue = QueueManager.factory(queue_kwargs)
            run_server(pipe, options, queue)
        except Exception as exc:
            options.logger.exception(f'Integration: Server error: {exc}', exc_info=True)

            if queue:
                queue.teardown()

        options.logger.info('Integration: Server stopped')
        options.teardown()
