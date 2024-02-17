import json
import multiprocessing
import time
from multiprocessing import Process
from multiprocessing.queues import JoinableQueue
from multiprocessing.synchronize import Lock
from pathlib import Path
from typing import Any

from amsdal_agent.queues.base import QueueBase


class PersistentQueue(QueueBase):
    def __init__(
        self,
        queue: JoinableQueue,  # type: ignore[type-arg]
        lock: Lock,
        persist_file_path: Path,
        save_interval: int = 60,
        max_buffer_size: int = 10,
    ) -> None:
        self.lock = lock
        self.queue = queue
        self.persist_file_path = persist_file_path
        self.save_interval = save_interval
        self.max_buffer_size = max_buffer_size
        self._persist_process: multiprocessing.Process | None = None

    def run_periodic_persist(
        self,
    ) -> Process:
        process = multiprocessing.Process(
            target=self._persist_periodic,
            args=(
                self.queue,
                self.lock,
                self.persist_file_path,
                self.save_interval,
            ),
            name='PersistentQueue',
        )
        process.start()
        self._persist_process = process

        return process

    def teardown(self) -> None:
        if self._persist_process:
            self._persist_process.terminate()
            self._persist_process.join()

    def put(self, item: Any) -> None:
        self.lock.acquire()
        self.queue.put(item)
        size = self.queue.qsize()
        self.lock.release()

        if size >= self.max_buffer_size:
            self._persist(self.queue, self.lock, self.persist_file_path)

    def acquire(self) -> None:
        self.lock.acquire()

    def release(self) -> None:
        self.lock.release()

    def get(self) -> Any:
        return self.queue.get()

    def task_done(self) -> None:
        self.queue.task_done()

    def task_failed(self, item: Any) -> None:
        ...

    @classmethod
    def _persist_periodic(
        cls,
        queue: JoinableQueue,  # type: ignore[type-arg]
        lock: Lock,
        file_path: Path,
        save_interval: int,
    ) -> None:
        while True:
            time.sleep(save_interval)
            cls._persist(queue, lock, file_path)

    @staticmethod
    def _persist(
        queue: JoinableQueue,  # type: ignore[type-arg]
        lock: Lock,
        file_path: Path,
    ) -> None:
        lock.acquire()

        if queue.empty():
            lock.release()
            return

        buffer = []

        while not queue.empty():
            buffer.append(queue.get())
            queue.task_done()

        try:
            file_path.write_text(json.dumps(buffer))
        finally:
            for item in buffer:
                queue.put(item)

            lock.release()
