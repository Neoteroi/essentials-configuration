import json
from typing import Any

from config.common.files import FileConfigurationSource


class JSONFile(FileConfigurationSource):
    def read_source(self) -> dict[str, Any]:
        with open(self.file_path, "rt", encoding="utf-8") as source:
            return json.load(source)
