import os
from typing import Any, Dict, Optional

from . import ConfigurationSource


class EnvironmentalVariables(ConfigurationSource):
    def __init__(self, prefix: Optional[str] = None, strip_prefix: bool = True) -> None:
        super().__init__()
        self.prefix = prefix
        self.strip_prefix = strip_prefix

    def get_values(self) -> Dict[str, Any]:
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
