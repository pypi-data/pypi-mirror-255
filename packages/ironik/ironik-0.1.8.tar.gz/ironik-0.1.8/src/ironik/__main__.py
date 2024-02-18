#!/usr/bin/env python
"""
Program and CLI initialization.

:author: Jonathan Decker
"""
import sys

from rich import traceback
from rich.console import Console

from ironik.cli import ironik_cli


def main() -> None:
    """ironik."""
    console = Console(file=sys.stderr)
    console.print(
        r"""[bold green]
          _                          _   _
         (_)  _ __    ___    _ __   (_) | | __
         | | | '__|  / _ \  | '_ \  | | | |/ /
         | | | |    | (_) | | | | | | | |   <
         |_| |_|     \___/  |_| |_| |_| |_|\_\
        In Rancher Openstack; Now Install Kubernetes
        """
    )
    ironik_cli.ironik_cli()


if __name__ == "__main__":
    traceback.install()
    main()  # pragma: no cover
