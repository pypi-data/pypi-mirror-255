import argparse
import sys
from pathlib import Path

from rich import print

from amsdal_agent.__about__ import __version__
from amsdal_agent.cli.supervisor import supervisor
from amsdal_agent.services.options import AmsdaldState


def render_help() -> None:
    print('AMSDAL Agent.')
    print(f'Agent Version: [bold green]{__version__}[/bold green]')
    print()
    print('Usage: [blue]amsdald COMMAND [OPTIONS][/blue]')
    print()
    print('Available commands:')
    print(' [blue]serve[/blue] - run agent')
    print(' [blue]restart[/blue] - restart agent')
    print(' [blue]stop[/blue] - stop agent')
    print()
    print('Use [blue]amsdald COMMAND --help[/blue] to see available options for specific command')


def main() -> None:
    if len(sys.argv) == 1:
        render_help()
        return

    parser = argparse.ArgumentParser(description='AMSDAL Agent.')
    command = sys.argv[1]

    if command == 'serve':
        _register_serve_args(parser)
        args = parser.parse_args(sys.argv[2:])
        serve(
            server_host=args.server_host,
            server_queue_host=args.server_queue_host,
            server_queue_dump_path=(
                Path(args.server_queue_dump_path) if args.server_queue_dump_path else Path('amsdald.queue.data')
            ),
            app_host=args.app_host,
            app_auth=args.app_auth,
            user=args.user,
            daemon=args.daemon,
            pid_file=Path(args.pid_file) if args.pid_file else Path('amsdald.pid'),
            umask=args.umask,
            log_level=args.log_level,
            log_file=Path(args.log_file) if args.log_file else Path('amsdald.log'),
            log_format=args.log_format,
            log_max_bytes=args.log_max_bytes,
            log_backup_count=args.log_backup_count,
        )
    elif command == 'restart':
        _register_restart_stop_args(parser)
        args = parser.parse_args(sys.argv[2:])
        restart(args.server_host)
    elif command == 'stop':
        _register_restart_stop_args(parser)
        args = parser.parse_args(sys.argv[2:])
        stop(args.server_host)
    else:
        render_help()


def _register_serve_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--server_host',
        '-sh',
        help='Server host to listen on.',
        default='localhost:8054',
    )
    parser.add_argument(
        '--server-queue-host',
        '-sqh',
        help='Queue host to connect to. If not provided, local queue will be used.',
        default=None,
    )
    parser.add_argument(
        '--server-queue-dump-path',
        '-sqdp',
        help=(
            'Path to file where the dump of queue will be persisted. '
            'By default it will be stored in the directory where agent is installed. '
            'If --server-queue-host specified, this option will be ignored.'
        ),
        default='amsdal_queue.data',
    )
    parser.add_argument(
        '--app-host',
        '-ah',
        help='Application host to send data to.',
        default='http://localhost:8000',
    )
    parser.add_argument(
        '--app-auth',
        '-aa',
        help='Application auth token to send data to.',
        default='',
    )
    parser.add_argument(
        '--user',
        '-u',
        help='User to run agent as (or numeric uid).',
        default=None,
    )
    parser.add_argument(
        '--daemon',
        '-d',
        action=argparse.BooleanOptionalAction,
        help='Run agent in daemon mode.',
        default=True,
    )
    parser.add_argument(
        '--pid-file',
        '-pf',
        help='PID file to use for the agent process.',
        default='amsdald.pid',
    )
    parser.add_argument(
        '--umask',
        '-um',
        help='Umask to use for the agent process.',
        default='022',
    )
    parser.add_argument(
        '--log-level',
        '-ll',
        help='Log level to use.',
        default='INFO',
    )
    parser.add_argument(
        '--log-file',
        '-lf',
        help='Log file to use.',
        default=None,
    )
    parser.add_argument(
        '--log-format',
        '-lfmt',
        help='Log format to use.',
        default='[%(asctime)s] %(levelname)-8s - %(message)s %(name)s.%(funcName)s:%(lineno)d',
    )
    parser.add_argument(
        '--log-max-bytes',
        '-lmb',
        help='Log max bytes.',
        default=1024 * 1024 * 10,
        type=int,
    )
    parser.add_argument(
        '--log-backup-count',
        '-lbc',
        help='Log backup count.',
        default=5,
        type=int,
    )


def _register_restart_stop_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--server-host',
        '-sh',
        help='Server host to listen on.',
        default='localhost:8054',
    )


def serve(
    # Server
    server_host: str,
    server_queue_host: str | None,
    server_queue_dump_path: Path,
    # Application
    app_host: str,
    app_auth: str,
    # Process
    user: str | None,
    daemon: bool,  # noqa: FBT001
    pid_file: Path,
    umask: str,
    # Logging
    log_level: str,
    log_file: Path | None,
    log_format: str,
    log_max_bytes: int,
    log_backup_count: int,
) -> None:
    """
    Run the agent.
    """
    options = None
    first = True
    log_file = log_file or Path('amsdald.log')

    while True:
        try:
            options = supervisor(
                first=first,
                server_host=server_host,
                server_queue_host=server_queue_host,
                server_queue_dump_path=server_queue_dump_path,
                app_host=app_host,
                app_auth=app_auth,
                user=user,
                daemon=daemon,
                pid_file=pid_file,
                umask=int(umask, 8),
                log_level=log_level,
                log_file=log_file,
                log_format=log_format,
                log_max_bytes=log_max_bytes,
                log_backup_count=log_backup_count,
            )
        except Exception as exc:
            print('Supervisor error: %s', exc)
            break
        else:
            options.logger.info('Supervisor exited with state: %s', options.state)

            if options.state < AmsdaldState.RESTARTING:
                break

    if options:
        options.logger.info('Supervisor shutdown')
        options.teardown()


def restart(
    server_host: str,
) -> None:
    import httpx

    response = httpx.post(f'http://{server_host}/action', content='RESTART')
    response.raise_for_status()


def stop(
    server_host: str,
) -> None:
    import httpx

    response = httpx.post(f'http://{server_host}/action', content='SHUTDOWN')
    response.raise_for_status()
