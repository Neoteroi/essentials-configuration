import json
import os
from typing import Any, Dict

from . import ConfigurationSource
from .errors import MissingConfigurationFileError


class JSONFile(ConfigurationSource):
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

        with open(self.file_path, "rt", encoding="utf-8") as source_file:
            return json.load(source_file)
