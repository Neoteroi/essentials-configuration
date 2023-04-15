import json
import os
import sys
from pathlib import Path
from typing import Optional

import rich_click as click

from config.common import apply_key_value
from config.user import UserSettings


class ClickLogger:
    def info(self, message):
        click.echo(message)

    def debug(self, message):
        if os.environ.get("EC_VERBOSE") == "1":
            click.echo(message)


class UserSettingsManager(UserSettings):
    def __init__(
        self,
        project_name: Optional[str] = None,
    ) -> None:
        super().__init__(project_name, True)
        self.logger = ClickLogger()

    def init_project_settings(self):
        name = self.project_name
        settings_path = self.settings_file_path

        if not settings_path.exists():
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.write_text("{}")

        self.logger.info(f"Initialized project settings for: {name}")
        self.logger.debug(f"settings path: {settings_path}")
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
            self.init_project_settings()
            self.write(values)

    def set_value(self, key: str, value: str):
        values = self.get_values()
        values = apply_key_value(values, key, value)
        self._write_values(values)

    def get_value(self, key: str):
        values = self.get_values()
        if key in values:
            self.logger.info(values[key])

    def set_many_values(self, data):
        values = self.get_values()
        values.update(data)
        self._write_values(values)

    def show_settings(self):
        values = self.get_values()
        self.logger.info(
            json.dumps(values, indent=4, ensure_ascii=True, sort_keys=True)
        )

    def del_value(self, key: str):
        if not self.settings_file_path.exists():
            self.logger.info("There are no settings configured.")
            return
        values = self.get_values()
        try:
            del values[key]
        except KeyError:
            pass
        else:
            self.write(values)

    def write(self, values):
        self.settings_file_path.write_text(
            json.dumps(values, indent=4, ensure_ascii=False, sort_keys=True),
            encoding="utf8",
        )
        self.logger.debug(f"Updated file: {self.settings_file_path}")

    def list_projects(self):
        try:
            for child in self.get_base_folder().iterdir():
                if child.is_dir():
                    self.logger.info(child.name)
        except FileNotFoundError:  # pragma: no cover
            self.logger.info("There are no settings configured.")

    def show_info(self):
        if self.settings_file_path.exists():
            self.logger.info(f"settings are stored at: {self.settings_file_path}")
        else:
            self.logger.info("There is no settings file configured.")


@click.group()
def settings():
    """
    Commands to handle user settings, stored in the user's folder.
    """


@click.command(name="init")
@click.option("--project", "-p", required=False)
def init_settings(project: Optional[str]):
    """
    Initialize user settings for the current folder.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.
    """
    UserSettingsManager(project).init_project_settings()


@click.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--project", "-p", required=False)
def set_value(key: str, value: str, project: Optional[str]):
    """
    Set a setting in a user file by key and value.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config settings set "some" "example"

    config settings set "some" "example" -p "foo"
    """
    UserSettingsManager(project).set_value(key, value)


@click.command(name="get")
@click.argument("key")
@click.option("--project", "-p", required=False)
def get_value(key: str, project: Optional[str]):
    """
    Get a setting in a user file by key.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config settings get "key"
    """
    UserSettingsManager(project).get_value(key)


@click.command(name="set-many")
@click.option("--file", help="Input file", type=click.File("r"), default=sys.stdin)
@click.option("--project", "-p", required=False)
def set_many_values(file, project: Optional[str]):
    """
    Set many settings, read from a JSON file passed through stdin.
    If a project name is specified, it is used, otherwise a value is obtained
    from a `pyproject.toml` file, or generated.

    Examples:

    config settings set-many --file example.json

    config settings set-many < example.json
    """
    with file:
        data = json.loads(file.read())

    UserSettingsManager(project).set_many_values(data)


@click.command(name="del")
@click.argument("key")
@click.option("--project", "-p", required=False)
def del_value(key: str, project: Optional[str]):
    """
    Delete a setting for a project, by key.
    """
    UserSettingsManager(project).del_value(key)


@click.command(name="show")
@click.option("--project", "-p", required=False)
def show_settings(project: Optional[str]):
    """
    Show the local settings for a project.
    """
    UserSettingsManager(project).show_settings()


@click.command(name="list")
def list_groups():
    """
    List all projects configured for settings stored in the user folder.
    """
    UserSettingsManager(None).list_projects()


@click.command(name="info")
@click.option("--project", "-p", required=False)
def show_info(project: Optional[str]):
    """
    Show information about settings for a project.
    """
    UserSettingsManager(project).show_info()


settings.add_command(init_settings)
settings.add_command(get_value)
settings.add_command(set_value)
settings.add_command(set_many_values)
settings.add_command(del_value)
settings.add_command(show_settings)
settings.add_command(list_groups)
settings.add_command(show_info)
