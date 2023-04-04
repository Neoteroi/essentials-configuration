from typing import Any, Callable, Dict

from config.common.files import FileConfigurationSource, PathType

try:
    # Python 3.11
    import tomllib
except ImportError:  # pragma: no cover
    # older Python
    import tomli as tomllib  # noqa


class TOMLFile(FileConfigurationSource):
    def __init__(
        self,
        file_path: PathType,
        optional: bool = False,
        parse_float: Callable[[str], Any] = float,
    ) -> None:
        super().__init__(file_path, optional)
        self.parse_float = parse_float

    def read_source(self) -> Dict[str, Any]:
        with open(self.file_path, "rb") as source:
            return tomllib.load(source, parse_float=self.parse_float)
