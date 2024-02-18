from typing import Any
from typing import ClassVar

from amsdal_agent.queues.base import QueueBase
from amsdal_agent.services.options import AmsdaldOptions


class QueueManager:
    _queue_kwargs: ClassVar[dict[str, Any] | None] = None

    @classmethod
    def init_write_queue_kwargs(cls, options: AmsdaldOptions, manager: Any) -> None:
        if options.server_queue_host:
            cls._queue_kwargs = {
                'url': options.server_queue_host,
            }
        else:
            cls._queue_kwargs = {
                'queue': manager.JoinableQueue(),
                'lock': manager.Lock(),
                'persist_file_path': options.server_queue_dump_path,
            }

    @classmethod
    def get_queue_kwargs(cls) -> dict[str, str]:
        if cls._queue_kwargs is None:
            msg = 'QueueManager has not been initialized'
            raise Exception(msg)
        return cls._queue_kwargs

    @staticmethod
    def factory(kwargs: dict[str, Any]) -> QueueBase:
        if 'url' in kwargs:
            from amsdal_agent.queues.redis_queue import RedisQueue

            return RedisQueue(**kwargs)
        else:
            from amsdal_agent.queues.persistent_queue import PersistentQueue

            queue = PersistentQueue(**kwargs)

            return queue
