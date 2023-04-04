import logging

import click

from config.cli.commands.secrets import secrets


@click.group()
@click.option(
    "--verbose", default=False, help="Whether to display debug output.", is_flag=True
)
def main(verbose: bool):
    """
    essentials-configuration CLI
    """
    from config.cli.logs import logger

    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Running in --verbose mode")


main.add_command(secrets)
