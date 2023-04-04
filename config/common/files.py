from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, Union

from config.common import ConfigurationSource
from config.errors import MissingConfigurationFileError

PathType = Union[Path, str]


class FileConfigurationSource(ConfigurationSource):
    def __init__(self, file_path: PathType, optional: bool = False) -> None:
        super().__init__()
        self.file_path = Path(file_path)
        self.optional = optional

    @abstractmethod
    def read_source(self) -> Dict[str, Any]:
        """
        Reads values from the source file path. This method is not
        used if the file does not exist.
        """

    def get_values(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            if self.optional:
                return {}
            raise MissingConfigurationFileError(self.file_path)
        return self.read_source()
