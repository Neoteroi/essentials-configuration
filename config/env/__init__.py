import os
from typing import Any

from dotenv import load_dotenv

from config.common import ConfigurationSource
from config.common.files import PathType


class EnvironmentVariables(ConfigurationSource):
    def __init__(
        self,
        prefix: str | None = None,
        strip_prefix: bool = True,
        file: PathType | None = None,
    ) -> None:
        super().__init__()
        self.prefix = prefix
        self.strip_prefix = strip_prefix
        self._file = file

    def get_values(self) -> dict[str, Any]:
        if self._file:
            load_dotenv(self._file)

        values = {}
        prefix = self.prefix
        strip_prefix = self.strip_prefix
        if prefix:
            prefix = prefix.lower()
        for key, value in os.environ.items():
            key_lower = key.lower()
            if prefix and not key_lower.startswith(prefix):
                continue
            if prefix and strip_prefix:
                key_lower = key_lower[len(prefix) :]
            values[key_lower] = value
        return values


EnvVars = EnvironmentVariables
