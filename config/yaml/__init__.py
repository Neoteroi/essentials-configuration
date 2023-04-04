from typing import Any, Dict

import yaml

from config.common.files import FileConfigurationSource, PathType


class YAMLFile(FileConfigurationSource):
    def __init__(
        self, file_path: PathType, optional: bool = False, safe_load: bool = True
    ) -> None:
        super().__init__(file_path, optional)
        self.safe_load = safe_load

    def read_source(self) -> Dict[str, Any]:
        with open(self.file_path, "rt", encoding="utf-8") as source:
            if self.safe_load:
                return yaml.safe_load(source)
            return yaml.full_load(source)
