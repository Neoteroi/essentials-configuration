import json
import sys
from typing import Optional

import click

from config.secrets import UserSecretsManager


def _strip(value):
    if "'" in value:
        return value.strip("'")
    return value


@click.group()
def secrets():
    """
    Commands to handle user secrets.
    """


@click.command(name="init")
@click.option("--project", "-p", required=False)
def init_secrets(project: Optional[str]):
    """
    Initialize user secrets for the current folder.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.
    """
    UserSecretsManager(project).init_project_secrets()


@click.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--project", "-p", required=False)
def set_secret(key: str, value: str, project: Optional[str]):
    """
    Set a secret in a user file by key and value.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config secrets set "some" "example"

    config secrets set "some" "example" -p "foo"
    """
    UserSecretsManager(project).set_secret(_strip(key), _strip(value))


@click.command(name="set-many")
@click.option("--file", help="Input file", type=click.File("r"), default=sys.stdin)
@click.option("--project", "-p", required=False)
def set_many_secrets(file, project: Optional[str]):
    """
    Set many secrets read from a JSON file passed through stdin.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config secrets set-many --file example.json

    config secrets set-many < example.json
    """
    with file:
        data = json.loads(file.read())

    UserSecretsManager(project).set_many_secrets(data)


@click.command(name="remove")
@click.argument("key")
@click.option("--project", "-p", required=False)
def remove_secret(key: str, project: Optional[str]):
    """
    Remove a secret for a project, by key.
    """
    UserSecretsManager(project).remove_secret(_strip(key))


@click.command(name="show")
@click.option("--project", "-p", required=False)
def show_secrets(project: Optional[str]):
    """
    Show the local secrets for a project.
    """
    UserSecretsManager(project).show_secrets()


@click.command(name="list")
def list_groups():
    """
    List all projects configured for secrets stored in the user folder.
    """
    UserSecretsManager(None).list_projects()


@click.command(name="info")
@click.option("--project", "-p", required=False)
def show_info(project: Optional[str]):
    """
    Show information about secrets for a project.
    """
    UserSecretsManager(project).show_info()


secrets.add_command(init_secrets)
secrets.add_command(set_secret)
secrets.add_command(set_many_secrets)
secrets.add_command(remove_secret)
secrets.add_command(show_secrets)
secrets.add_command(list_groups)
secrets.add_command(show_info)
