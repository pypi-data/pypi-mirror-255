import grp
import logging
import os
import pwd
import sys
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any
from typing import ClassVar


class AmsdaldState(int, Enum):
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


class AmsdaldOptions:
    _min_fds: ClassVar[int] = 1024

    _logger: logging.Logger | None = None
    _unlink_pidfile: bool = False

    def __init__(
        self,
        server_host: str,
        server_queue_host: str | None,
        server_queue_dump_path: Path,
        app_host: str,
        app_auth: str,
        user: str | None,
        daemon: bool,  # noqa: FBT001
        pid_file: Path | None,
        umask: int,
        log_file: Path | None,
        log_level: str,
        log_format: str,
        log_max_bytes: int,
        log_backup_count: int,
    ) -> None:
        self.server_host = server_host
        self.server_queue_host = server_queue_host
        self.server_queue_dump_path = server_queue_dump_path
        self.app_host = app_host
        self.app_auth = app_auth
        self.user = user
        self.daemon = daemon
        self.pid_file = pid_file
        self.umask = umask
        self.log_file = log_file
        self.log_level = log_level
        self.log_format = log_format
        self.log_max_bytes = log_max_bytes
        self.log_backup_count = log_backup_count

        self.state = AmsdaldState.RUNNING
        self.first = True
        self._parent_pid = None

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            msg = 'Options has not been initialized'
            raise Exception(msg)
        return self._logger

    def get_subprocess_init_kwargs(self, name: str) -> dict[str, Any]:
        if self.log_file is None:
            msg = 'Log file option is required'
            raise Exception(msg)

        if self.log_file.as_uri() == 'file:///dev/stdout':
            _log_file = self.log_file
        else:
            _log_file = self.log_file.parent / f'{name}_{self.log_file.name}'

        return {
            'server_host': self.server_host,
            'server_queue_host': self.server_queue_host,
            'server_queue_dump_path': self.server_queue_dump_path,
            'app_host': self.app_host,
            'app_auth': self.app_auth,
            'user': self.user,
            'daemon': False,
            'pid_file': None,
            'umask': self.umask,
            'log_file': _log_file,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'log_max_bytes': self.log_max_bytes,
            'log_backup_count': self.log_backup_count,
        }

    def setup(self) -> None:
        if not self.first:
            self._close_files()

        self._setup_logger()
        self._set_uid()

        if self.daemon:
            self._daemonize()
            self._write_pid_file()

    def teardown(self) -> None:
        self.logger.debug('Tearing down options...')

        if self._unlink_pidfile:
            self._unlink(self.pid_file)
            self._unlink_pidfile = False

        self.logger.debug('Teardown logger...')
        self._teardown_logger()

    def _close_files(self) -> None:
        start = 5
        os.closerange(start, self._min_fds)

    def _setup_logger(self) -> None:
        if self.log_file is None:
            return

        self._logger = logging.getLogger(self.log_file.stem)
        self._logger.setLevel(self.log_level)

        handler = None

        if self.log_file is not None:
            handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.log_max_bytes,
                backupCount=self.log_backup_count,
            )
        elif not self.daemon:
            from logging import StreamHandler

            handler = StreamHandler(sys.stdout)

        if handler is not None:
            formatter = logging.Formatter(self.log_format)
            handler.setFormatter(formatter)
            handler.setLevel(self.log_level)

            self._logger.addHandler(handler)

    def _teardown_logger(self) -> None:
        if not self._logger:
            return

        handlers = self._logger.handlers[:]

        for handler in handlers:
            try:
                self._logger.removeHandler(handler)
            except Exception as exc:
                self.logger.error('Cannot remove handler %s: %s', handler, exc)
            else:
                self.logger.info('Removed')

            if isinstance(handler, RotatingFileHandler):
                handler.close()

    def _set_uid(self) -> None:
        if self.user is None:
            if os.getuid() == 0:
                self._logger.warning(  # type: ignore[union-attr]
                    'amsdald is running as root.  '
                    'Privileges were not dropped because no user is '
                    'specified.  If you intend to run '
                    'as root, you can set user=root in the options '
                    'to avoid this message.'
                )
        else:
            msg = self._drop_privileges(self.user)

            if msg is None:
                self._logger.info('Set uid to user %s succeeded', self.user)  # type: ignore[union-attr]
            else:  # failed to drop privileges
                self.exit(msg)

    def _daemonize(self) -> None:
        pid = os.fork()

        if pid != 0:
            # Parent
            os._exit(0)  # pylint: disable=protected-access

        # child
        os.setsid()
        os.umask(self.umask)

        os.close(0)
        self.stdin = sys.stdin = sys.__stdin__ = open('/dev/null')  # type: ignore[misc]
        os.close(1)
        self.stdout = sys.stdout = sys.__stdout__ = open('/dev/null', 'w')  # type: ignore[misc]
        os.close(2)
        self.stderr = sys.stderr = sys.__stderr__ = open('/dev/null', 'w')  # type: ignore[misc]

    @staticmethod
    def _drop_privileges(user: str) -> str | None:
        if not user:
            return 'No user specified to setuid to!'

        try:
            uid = int(user)
            pwrec = pwd.getpwuid(uid)
        except (ValueError, KeyError):
            try:
                pwrec = pwd.getpwnam(user)
                uid = pwrec.pw_uid
            except KeyError:
                return f"Can't find user {user}"

        if os.getuid() == uid:
            return None

        if os.getuid() != 0:
            return "Can't drop privilege as nonroot user"

        gid = pwrec.pw_gid

        if hasattr(os, 'setgroups'):
            groups = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]
            groups.insert(0, gid)

            try:
                os.setgroups(groups)
            except OSError:
                return 'Could not set groups of effective user'

        try:
            os.setgid(gid)
            os.setuid(uid)
        except OSError:
            return 'Could not set group id or user id of effective user'

        return None

    def _write_pid_file(self) -> None:
        self.logger.debug('write pid file %s', self.pid_file)

        if not self.pid_file:
            if not self.daemon:
                self.logger.info('pid file is skipped')
                return None

            self.exit('pid file is required for daemon mode')

        pid = os.getpid()
        self.logger.info('pid %s', pid)

        try:
            self.pid_file.write_text('%s\n' % pid)  # type: ignore[union-attr]
        except (OSError, AttributeError):
            self._logger.critical('could not write pidfile %s', self.pid_file)  # type: ignore[union-attr]
        else:
            self._unlink_pidfile = True
            self._logger.info('amsdald started with pid %s', pid)  # type: ignore[union-attr]

    def _unlink(self, pid_file: Path | None) -> None:
        if not pid_file or not pid_file.exists():
            return None

        try:
            pid_file.unlink()
        except OSError:
            self._logger.warning('could not remove pidfile %s', pid_file)  # type: ignore[union-attr]

    def exit(self, msg: str) -> None:
        sys.stderr.write(f'Error: {msg}\n')
        sys.exit(2)
