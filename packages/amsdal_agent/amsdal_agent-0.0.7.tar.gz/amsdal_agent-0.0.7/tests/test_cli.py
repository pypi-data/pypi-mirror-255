import io
from contextlib import redirect_stdout

from amsdal_agent.__about__ import __version__
from amsdal_agent.cli import render_help

help_text = f"""AMSDAL Agent.
Agent Version: {__version__}

Usage: amsdald COMMAND [OPTIONS]

Available commands:
 serve - run agent
 restart - restart agent
 stop - stop agent

Use amsdald COMMAND --help to see available options for specific command
"""


def test_cli_help() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        render_help()

    assert buffer.getvalue() == help_text
