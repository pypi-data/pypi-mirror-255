import multiprocessing
import multiprocessing.connection
import os
from typing import Any

from amsdal_agent.queues.manager import QueueManager
from amsdal_agent.services.options import AmsdaldOptions
from amsdal_agent.services.worker import run_worker


class WorkerProcess:
    name = 'Amsdald Worker'

    def __init__(
        self,
        options: AmsdaldOptions,
    ) -> None:
        self.options = options
        self.process: multiprocessing.Process | None = None

    def start(self) -> None:
        self.process = multiprocessing.Process(
            target=self.worker,
            args=(
                self.options.get_subprocess_init_kwargs('worker'),
                QueueManager.get_queue_kwargs(),
            ),
            name=self.name,
        )
        self.process.start()

    def stop(self) -> None:
        if self.process:
            self.process.terminate()
            self.process.join()

    @staticmethod
    def worker(
        options_kwargs: dict[str, Any],
        queue_kwargs: dict[str, Any],
    ) -> None:
        options = AmsdaldOptions(**options_kwargs)
        queue = None

        try:
            options.setup()
            options.logger.info('Integration: Starting worker.... PID: %s', os.getpid())
            queue = QueueManager.factory(queue_kwargs, is_writing_mode=False)

            run_worker(options, queue)
        except Exception as exc:
            options.logger.exception(f'Integration: Worker error: {exc}', exc_info=True)

            if queue:
                queue.teardown()

        options.logger.info('Integration: Worker stopped')
        options.teardown()
