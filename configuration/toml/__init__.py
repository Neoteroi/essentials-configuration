import os
from typing import Any, Callable, Dict

try:
    # Python 3.11
    import tomllib
except ImportError:  # pragma: no cover
    # older Python
    import tomli as tomllib  # noqa

from configuration.common import ConfigurationSource
from configuration.errors import MissingConfigurationFileError


class TOMLFile(ConfigurationSource):
    def __init__(
        self,
        file_path: str,
        optional: bool = False,
        parse_float: Callable[[str], Any] = float,
    ) -> None:
        super().__init__()
        self.file_path = file_path
        self.optional = optional
        self.parse_float = parse_float

    def get_values(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            if self.optional:
                return {}
            raise MissingConfigurationFileError(self.file_path)

        with open(self.file_path, "rb") as source:
            return tomllib.load(source, parse_float=self.parse_float)
