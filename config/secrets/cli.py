import json
import os
import sys
from pathlib import Path
from typing import Optional

import click

from config.common import apply_key_value
from config.secrets import UserSecrets

try:
    # Python 3.11
    import tomllib
except ImportError:  # pragma: no cover
    # older Python
    import tomli as tomllib  # noqa


class ClickLogger:
    def info(self, message):
        click.echo(message)

    def debug(self, message):
        if os.environ.get("EC_VERBOSE") == "1":
            click.echo(message)


class UserSecretsManager(UserSecrets):
    def __init__(
        self,
        project_name: Optional[str] = None,
    ) -> None:
        super().__init__(project_name, True)
        self.logger = ClickLogger()

    def init_project_secrets(self):
        name = self.project_name
        secrets_path = self.secrets_file_path

        if not secrets_path.exists():
            secrets_path.parent.mkdir(parents=True, exist_ok=True)
            secrets_path.write_text("{}")

        self.logger.info(f"Initialized project secrets for: {name}")
        self.logger.debug(f"Secrets path: {secrets_path}")
        pyproject = Path("pyproject.toml")

        if not pyproject.exists():
            pyproject.write_text(
                f"""
[project]
name = "{name}"
                """.strip()
                + "\n",
                encoding="utf8",
            )

    def _write_values(self, values):
        try:
            self.write(values)
        except FileNotFoundError:
            self.init_project_secrets()
            self.write(values)

    def set_secret(self, key: str, value: str):
        values = self.get_values()
        values = apply_key_value(values, key, value)
        self._write_values(values)

    def get_secret(self, key: str):
        values = self.get_values()
        if key in values:
            self.logger.info(values[key])

    def set_many_secrets(self, data):
        values = self.get_values()
        values.update(data)
        self._write_values(values)

    def show_secrets(self):
        values = self.get_values()
        self.logger.info(
            json.dumps(values, indent=4, ensure_ascii=True, sort_keys=True)
        )

    def del_secret(self, key: str):
        if not self.secrets_file_path.exists():
            self.logger.info("There are no secrets configured.")
            return
        values = self.get_values()
        try:
            del values[key]
        except KeyError:
            pass
        else:
            self.write(values)

    def write(self, values):
        self.secrets_file_path.write_text(
            json.dumps(values, indent=4, ensure_ascii=False, sort_keys=True),
            encoding="utf8",
        )
        self.logger.debug(f"Updated file: {self.secrets_file_path}")

    def list_projects(self):
        try:
            for child in self.get_base_folder().iterdir():
                if child.is_dir():
                    self.logger.info(child.name)
        except FileNotFoundError:  # pragma: no cover
            self.logger.info("There are no secrets configured.")

    def show_info(self):
        if self.secrets_file_path.exists():
            self.logger.info(f"Secrets are stored at: {self.secrets_file_path}")
        else:
            self.logger.info("There is no secrets file configured.")


@click.group()
def secrets():
    """
    Commands to handle user secrets, for local development.
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
    UserSecretsManager(project).set_secret(key, value)


@click.command(name="get")
@click.argument("key")
@click.option("--project", "-p", required=False)
def get_secret(key: str, project: Optional[str]):
    """
    Get a secret in a user file by key.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config secrets get "key"
    """
    UserSecretsManager(project).get_secret(key)


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


@click.command(name="del")
@click.argument("key")
@click.option("--project", "-p", required=False)
def del_secret(key: str, project: Optional[str]):
    """
    Delete a secret for a project, by key.
    """
    UserSecretsManager(project).del_secret(key)


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
secrets.add_command(get_secret)
secrets.add_command(set_secret)
secrets.add_command(set_many_secrets)
secrets.add_command(del_secret)
secrets.add_command(show_secrets)
secrets.add_command(list_groups)
secrets.add_command(show_info)
