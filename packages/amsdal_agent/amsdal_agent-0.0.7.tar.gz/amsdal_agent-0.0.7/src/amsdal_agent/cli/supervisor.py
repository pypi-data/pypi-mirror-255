import multiprocessing
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from amsdal_agent.constants import RESTART_ACTION
from amsdal_agent.constants import SHUTDOWN_ACTION
from amsdal_agent.processes.server_process import ServerProcess
from amsdal_agent.processes.worker_process import WorkerProcess
from amsdal_agent.queues.manager import QueueManager
from amsdal_agent.services.options import AmsdaldOptions
from amsdal_agent.services.options import AmsdaldState


def supervisor(
    first: bool = True,  # noqa: FBT001 FBT002
    server_host: str = 'localhost:8054',
    server_queue_host: str | None = None,
    server_queue_dump_path: Path = Path('queue.data'),
    app_host: str = 'http://localhost:8080',
    app_auth: str = '',
    user: str | None = None,
    daemon: bool = True,  # noqa: FBT001 FBT002
    pid_file: Path = Path('amsdald.pid'),
    umask: int = 0o002,
    log_file: Path = Path('amsdald.log'),
    log_level: str = 'DEBUG',
    log_format: str = '%(asctime)s %(levelname)s %(message)s',
    log_max_bytes: int = 1024 * 1024 * 10,
    log_backup_count: int = 5,
) -> AmsdaldOptions:
    options = AmsdaldOptions(
        server_host=server_host,
        server_queue_host=server_queue_host,
        server_queue_dump_path=server_queue_dump_path,
        app_host=app_host,
        app_auth=app_auth,
        user=user,
        daemon=daemon,
        pid_file=pid_file,
        umask=umask,
        log_file=log_file,
        log_level=log_level,
        log_format=log_format,
        log_max_bytes=log_max_bytes,
        log_backup_count=log_backup_count,
    )
    options.first = first
    options.setup()

    manager = multiprocessing.Manager()
    QueueManager.init_write_queue_kwargs(options, manager)
    thread_errors: list[Any] = []

    def start() -> tuple[Any, Callable[[], None]]:
        options.logger.info('Integration: Starting sub-processes...')
        _stop_event = threading.Event()

        _server_process = ServerProcess(options)
        _worker_process = WorkerProcess(options)

        server_thread = threading.Thread(
            target=monitor_process,
            args=(
                options,
                _server_process,
                thread_errors,
                _stop_event,
            ),
            daemon=True,
        )

        worker_thread = threading.Thread(
            target=monitor_process,
            args=(
                options,
                _worker_process,
                thread_errors,
                _stop_event,
            ),
            daemon=True,
        )

        # start threads
        server_thread.start()
        worker_thread.start()

        def _stop() -> None:
            options.logger.info('Integration: Stopping sub-processes...')
            _stop_event.set()
            options.logger.debug('Integration: Joining server thread...')
            server_thread.join()
            worker_thread.join()
            options.logger.debug('Integration: Joining done...')
            _server_process.close_pipes()

        return _server_process.read_pipe, _stop

    action_read_pipe, stop = start()

    options.logger.info('Integration: Press Ctrl+C to exit')

    while True:
        try:
            time.sleep(1)

            if thread_errors:
                # some of the subprocesses were terminated
                options.logger.error('Integration: Thread errors: %s', thread_errors)
                options.logger.warning('Integration: Restarting...')
                options.state = AmsdaldState.FATAL
                stop()
                options.logger.info('Integration: Restarting...')

                break

            options.logger.debug('Integration: Checking for action...')

            if action_read_pipe.poll():
                try:
                    action_message = action_read_pipe.recv()
                except EOFError as exc:
                    options.logger.error('Integration: EOFError: %s', exc)
                    options.state = AmsdaldState.RESTARTING
                    stop()

                    raise

                options.logger.debug('Integration: Action found: %s', action_message)

                if action_message == RESTART_ACTION:
                    options.state = AmsdaldState.RESTARTING
                    stop()
                    options.logger.info('Integration: Restarting...')

                    break
                elif action_message == SHUTDOWN_ACTION:
                    options.state = AmsdaldState.SHUTDOWN
                    stop()
                    options.logger.info('Integration: Shutdown...')

                    break
            else:
                options.logger.debug('Integration: No action found')
        except KeyboardInterrupt:
            options.logger.info('Integration: Stopping agent...')
            stop()

            break

    options.logger.debug('Integration: End supervisor loop')
    manager.shutdown()

    return options


def monitor_process(
    options: AmsdaldOptions,
    process: ServerProcess | WorkerProcess,
    thread_errors: list[Exception],
    stop_event: threading.Event,
) -> None:
    options.logger.info('Integration: Monitor process for "%s" starting...', process.name)

    try:
        while not stop_event.is_set():
            options.logger.info(
                'Integration: Monitor process for "%s" is alive: %s',
                process.name,
                process.process and process.process.is_alive() or 'N/A',
            )

            if not process.process or not process.process.is_alive():
                process.start()

            time.sleep(5)
    except Exception as exc:
        thread_errors.append(exc)

    process.stop()
    options.logger.info('Integration: Monitor process stopped for "%s"', process.name)
