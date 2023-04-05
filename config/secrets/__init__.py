"""
This module provides support for user secrets stored locally.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from config.common import ConfigurationSource, apply_key_value
from config.json import JSONFile

try:
    # Python 3.11
    import tomllib
except ImportError:  # pragma: no cover
    # older Python
    import tomli as tomllib  # noqa


class UserSecrets(ConfigurationSource):
    """
    Reads values stored in a file inside the user's folder.
    """

    def __init__(
        self, project_name: Optional[str] = None, optional: bool = True
    ) -> None:
        """
        Configures an instance of UserSecrets that obtains values from a project file
        stored in the user's folder. If a project name is not provided, it is
        automatically inferred from a `pyproject.toml` file, if present, otherwise a
        random value is generated.
        """
        if not project_name:
            project_name = get_project_name()
        self.project_name = project_name
        self._secrets_file_path = self.get_base_folder() / project_name / "secrets.json"
        self._source = JSONFile(self.secrets_file_path, optional)

    def get_base_folder(self) -> Path:
        return Path.home() / ".neoteroi" / "ec"

    @property
    def secrets_file_path(self) -> Path:
        return self._secrets_file_path

    def get_values(self) -> Dict[str, Any]:
        """Returns the values read from this source."""
        return self._source.get_values()


def get_project_name() -> Optional[str]:
    pyproject = Path("pyproject.toml").resolve()

    if pyproject.exists():
        with open(pyproject, "rb") as source:
            data = tomllib.load(source)
        project = data.get("project")
        name = project.get("name")
        if name:
            return name

    return uuid4().hex


class UserSecretsManager(UserSecrets):
    def __init__(
        self,
        project_name: Optional[str] = None,
    ) -> None:
        super().__init__(project_name, True)
        self._logger = logging.getLogger("neoteroi-conf")

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def init_project_secrets(self):
        name = self.project_name
        secrets_path = self.secrets_file_path

        if not secrets_path.exists():
            secrets_path.parent.mkdir(parents=True, exist_ok=True)
            secrets_path.write_text("{}")

        self.logger.info("Initialized project secrets for: %s", name)
        self.logger.debug("Secrets path: %s", secrets_path)
        pyproject = Path("pyproject.toml")

        if not pyproject.exists():
            pyproject.write_text(
                f"""
    [project]
    name = "{name}"
                """.lstrip(),
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

    def set_many_secrets(self, data):
        values = self.get_values()
        values.update(data)
        self._write_values(values)

    def show_secrets(self):
        values = self.get_values()
        self.logger.info(
            json.dumps(values, indent=4, ensure_ascii=True, sort_keys=True)
        )

    def remove_secret(self, key: str):
        if not self.secrets_file_path.exists():
            self.logger.info("There are no secrets configured.")
            return
        values = self.get_values()
        try:
            del values[key]
        except KeyError:
            pass

        self.write(values)

    def write(self, values):
        self.secrets_file_path.write_text(
            json.dumps(values, indent=4, ensure_ascii=False, sort_keys=True),
            encoding="utf8",
        )
        self.logger.debug("Updated file: %s", self.secrets_file_path)

    def list_projects(self):
        try:
            for child in self.get_base_folder().iterdir():
                if child.is_dir():
                    self.logger.info(child.name)
        except FileNotFoundError:
            self.logger.info("There are no secrets configured.")

    def show_info(self):
        if self.secrets_file_path.exists():
            self.logger.info(
                "Secrets are stored at: %s",
                self.secrets_file_path,
            )
        else:
            self.logger.info("There is no secrets file configured.")
