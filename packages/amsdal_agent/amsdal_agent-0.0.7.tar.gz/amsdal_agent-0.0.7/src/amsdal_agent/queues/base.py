from abc import ABC
from abc import abstractmethod
from typing import Any


class QueueBase(ABC):
    @abstractmethod
    def put(self, item: Any) -> None:
        ...

    @abstractmethod
    def task_done(self) -> None:
        ...

    @abstractmethod
    def task_failed(self, item: Any) -> None:
        ...

    @abstractmethod
    def get(self) -> Any:
        ...

    @abstractmethod
    def teardown(self) -> None:
        ...
