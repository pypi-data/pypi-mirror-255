import json
from typing import Any

import redis

from amsdal_agent.queues.base import QueueBase


class RedisQueue(QueueBase):
    def __init__(self, url: str) -> None:
        self.redis = redis.from_url(url)

    def put(self, item: Any) -> None:
        self.redis.rpush('queue', json.dumps(item))

    def task_done(self) -> None:
        ...

    def task_failed(self, item: Any) -> None:
        self.redis.lpush('queue', json.dumps(item))

    def get(self) -> Any:
        return json.loads(self.redis.lpop('queue'))

    def teardown(self) -> None:
        self.redis.close()
