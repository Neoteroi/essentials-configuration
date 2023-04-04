import json
from typing import Any, Dict

from config.common.files import FileConfigurationSource


class JSONFile(FileConfigurationSource):
    def read_source(self) -> Dict[str, Any]:
        with open(self.file_path, "rt", encoding="utf-8") as source:
            return json.load(source)
