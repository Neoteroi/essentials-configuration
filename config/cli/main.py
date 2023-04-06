import os

import click

from config.secrets.cli import secrets


@click.group()
@click.option(
    "--verbose", default=False, help="Whether to display debug output.", is_flag=True
)
def main(verbose: bool):
    """
    essentials-configuration CLI
    """

    if verbose:
        os.environ["EC_VERBOSE"] = "1"


main.add_command(secrets)
