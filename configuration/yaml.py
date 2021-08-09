import os
from typing import Any, Dict

import yaml

from . import ConfigurationSource
from .errors import MissingConfigurationFileError


class YAMLFile(ConfigurationSource):
    def __init__(
        self, file_path: str, optional: bool = False, safe_load: bool = True
    ) -> None:
        super().__init__()
        self.file_path = file_path
        self.optional = optional
        self.safe_load = safe_load

    def get_values(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            if self.optional:
                return {}
            raise MissingConfigurationFileError(self.file_path)

        with open(self.file_path, "rt", encoding="utf-8") as f:
            if self.safe_load:
                data = yaml.safe_load(f)
            else:
                data = yaml.full_load(f)

            return data
