"""
This module provides support for user secrets stored locally, for development.
"""
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from config.common import ConfigurationSource
from config.json import JSONFile

try:
    # Python 3.11
    import tomllib
except ImportError:  # pragma: no cover
    # older Python
    import tomli as tomllib  # noqa


def get_project_name() -> str:
    pyproject = Path("pyproject.toml").resolve()

    if pyproject.exists():
        with open(pyproject, "rb") as source:
            data = tomllib.load(source)
        try:
            return data["project"]["name"]
        except KeyError:  # pragma: no cover
            pass

    return uuid4().hex


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
