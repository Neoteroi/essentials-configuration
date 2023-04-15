import os

import rich_click as click

from config.user.cli import settings


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


main.add_command(settings)
